import sys
import os

from pathlib import Path
Path(__file__).resolve()

from PyQt5.QtWidgets import QApplication
from ..Process.dg_process import DG_Process

from .DataFaceDoc import DataFaceDoc
from .DataFaceView import DataFaceView


def run_frontend(params={}):
    print("running run_frontend")
    app = QApplication(sys.argv)

    if 'Doc' not in params or 'View' not in params:
        print("run_frontend: No Doc or View in kwargs")
        return

    Doc = params['Doc']
    View = params['View']

    view = View()
    doc = Doc(params)

    view.attach_doc(doc)
    view.show()

    doc.start()
    app.exec_()

class DataFaceFrontend(DG_Process):
    def __init__(self, config):
        params = {'Doc': DataFaceDoc, 'View': DataFaceView, 'config': config}
        super(DataFaceFrontend, self).__init__("labeller", run_frontend, params=params)






