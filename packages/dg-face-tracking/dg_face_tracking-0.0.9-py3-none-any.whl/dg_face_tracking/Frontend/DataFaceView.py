import sys
import os
import time
import numpy as np
import qimage2ndarray
import uuid

import cv2

from pathlib import Path
Path(__file__).resolve()

from queue import Queue as _Queue

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QFrame, QLineEdit, QLabel, QCheckBox, QVBoxLayout, QFileDialog

from ..Data.face_data import FrameData, EmbeddedFaceData, LabelData
from .main_window import Ui_MainWindow


class DisplayImageWidget(QtWidgets.QWidget):
    """
    Custom widget to display:
    - Face image
    - Name of a person
    - Checkbox: is it a newly encountered person
    """
    def __init__(self, parent=None):
        super(DisplayImageWidget, self).__init__(parent)
        # Face name edit
        self.face_name_text_edit = QLineEdit()
        self.face_name_text_edit.setFrame(True)
        # Face score
        self.score_label = QLabel("")
        # Face image
        self.image_frame = QLabel()
        # New face checkbox
        self.new_face_chk = QCheckBox("New Face")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_frame)
        self.layout.addWidget(self.face_name_text_edit)
        self.layout.addWidget(self.score_label)
        self.setLayout(self.layout)

    def set_face_name(self, face_name: str):
        self.face_name_text_edit.setText(face_name)

    def get_face_name(self):
        return self.face_name_text_edit.text()

    def set_score(self, score):
        self.score_label.setText("score: " + str(score))

    def set_image(self, cv2_image):
        image = qimage2ndarray.array2qimage(cv2_image).rgbSwapped()
        self.image_frame.setPixmap(QtGui.QPixmap.fromImage(image))

    def clear(self):
        self.face_name_text_edit.setText("")
        self.score_label.setText("")
        pixmap = QtGui.QPixmap(1, 1)
        self.image_frame.setPixmap(pixmap)


class DataFaceView(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(DataFaceView, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.image_widget = DisplayImageWidget(self)
        self.facesLayout.addWidget(self.image_widget)
        self.image_widget.show()

        self.doc = None

        self.timer = QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_view)
        self.timer.start()


    def closeEvent(self, event):
        if self.doc:
            self.doc.stop()
        event.accept()

    def attach_doc(self, doc):
        self.doc = doc

    def clear(self):
        self.image_widget.clear()
        self.logTextEdit.setText("")

    def update_view(self):
        self.timer.stop()
        if not self.get_face_data():
            self.timer.start()

        if self.doc is not None:
            self.logTextEdit.setText(self.doc.log)
            self.answerTextEdit.setText(self.doc.prompt_answer)
            self.setPromptResult(self.doc.prompt_result)

    def setPromptResult(self, prompt_result):
        if prompt_result == 0:
            self.infoLabel.setStyleSheet("background-color: rgb(255, 255, 127);")
            self.infoLabel.setText("Analyzing...")
        elif prompt_result > 0:
            self.infoLabel.setStyleSheet("background-color: rgb(255, 0, 0);")
            self.infoLabel.setText("Detected!")
        elif prompt_result < 0:
            self.infoLabel.setStyleSheet("background-color: rgb(125, 125, 125);")
            self.infoLabel.setText("No detection")

    def on_okButton_pressed(self):
        label_data: LabelData = self.get_labelling()
        self.doc.publish(label_data)
        self.clear()
        self.timer.start()

    def on_skipButton_pressed(self):
        self.doc.publish(None)
        self.clear()
        self.timer.start()

    def on_LoadButton_pressed(self):
        fname = QFileDialog.getOpenFileName(self, 'Load Image',
                                            '', "Image files (*.jpg *.png)")
        if fname:
            face_image = cv2.imread(fname[0])
            self.doc.add_face_data(face_image)

        self.clear()
        self.timer.start()

    def on_applyBtn_pressed(self):
        self.doc.prompt = self.promptTextEdit.toPlainText()
        self.doc.prompt_result = 0
        print(f"A new prompt: {self.doc.prompt}")
        """
        if self.doc.prompt_result == 0:
            self.doc.prompt_result = 1
        else:
            self.doc.prompt_result = -self.doc.prompt_result
        self.timer.start()
        """

    def get_face_data(self):
        """
        Get faces from DataFaceDoc and fill array of DisplayImageWidget
        :returns : can_proceed : bool  Indicates if we can proceed to next frame, or some labelling is needed
        """
        face_data: LabelData = self.doc.face_data
        if face_data is None:
            return False

        face_uuid = face_data.get_face_uuid()
        face_name = face_data.get_label()
        score     = face_data.get_score()

        self.image_widget.set_face_name(face_name)
        self.image_widget.set_score(score)

        face_image = face_data.get_face_image()
        if face_image is not None:
            self.image_widget.set_image(face_image)

        return True

    def get_labelling(self):
        """
         Get labelling from DisplayImageWidget and add it to faces data
         skip: if true, then no need to write to db
        """
        if self.doc.face_data is not None:
            label_data = LabelData()
            label_data.from_data(self.doc.face_data)
            label = self.image_widget.get_face_name()
            label_data.set_label(label)
            return label_data
        else:
            return None




