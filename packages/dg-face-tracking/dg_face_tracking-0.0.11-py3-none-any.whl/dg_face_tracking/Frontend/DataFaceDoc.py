import multiprocessing
import threading
import time
from datetime import datetime
import numpy as np

from queue import Queue, Empty
from typing import Optional, List

import sys
import os
import cv2
from PIL import Image, PngImagePlugin

import google.generativeai as genai

import degirum as dg
import mytools

from pathlib import Path
Path(__file__).resolve()

from ..config_rt import ConfigRT

from ..Data.face_data import FaceData, LabelData
from ..Processors.lancedb_searcher import LanceDBSearcher
from ..Consumers.lancedb_writer import LanceDBWriter
from ..DataSource.DatasetSource import DatasetSource
from ..Processors.deepface_embedder import DeepfaceEmbedder

IMAGE_WIDTH = 512


def preprocess_stop_sequences(stop_sequences: str) -> Optional[List[str]]:
    if not stop_sequences:
        return None
    return [sequence.strip() for sequence in stop_sequences.split(",")]

def preprocess_image(image: Image.Image) -> Optional[Image.Image]:
    image_height = int(image.height * IMAGE_WIDTH / image.width)
    return image.resize((IMAGE_WIDTH, image_height))

def gemini(
    google_key: str,
    image_prompt: Optional[Image.Image],
    text_prompt: str,
    temperature: float = 0.4,
    max_output_tokens: int = 1024,
    stop_sequences: str = "",
    top_k: int = 32,
    top_p: float = 1.0,
):
    if not google_key:
        raise ValueError("GOOGLE_CLOUD_TOKEN is not set")
    try:
        genai.configure(api_key=google_key)
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            stop_sequences=preprocess_stop_sequences(stop_sequences=stop_sequences),
            top_k=top_k,
            top_p=top_p)

        if image_prompt is None:
            model = genai.GenerativeModel('gemini-pro')
        else:
            model = genai.GenerativeModel('gemini-pro-vision')

        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Sending a prompt: {text_prompt} ")
        image_prompt = preprocess_image(image_prompt)
        response = model.generate_content(
            [text_prompt, image_prompt] if image_prompt is not None else text_prompt,
            stream=False,
            generation_config=generation_config)

        # Concatenate the generated content to form a single string
        generated_text = ''.join(chunk.text for chunk in response)
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Got answer: {generated_text} ")
        return (text_prompt, generated_text)

    except Exception as e:
        print(f"An error occurred: {e}")
        return ""


def get_face_img(src_image, bbox: List[int], landmarks: List[int] = None):

    if landmarks is not None:
        face_shift = np.array([bbox[0], bbox[1]])

        flt = lambda feature: [lm['landmark'] for lm in landmarks if lm['label'] == feature][0]
        src_face_mask = np.array([flt('LeftEye'),
                                  flt('RightEye'),
                                  flt('Nose'),
                                  flt('LipsleftCorner'),
                                  flt('LipsRightCorner')])

        dst_face_mask = np.array(
            [[38.2946, 51.6963], [73.5318, 51.5014], [56.0252, 71.7366],
             [41.5493, 92.3655], [70.7299, 92.2041]],
            dtype=np.float32)
        dst_face_mask += face_shift

        d = 15
        dst_face_mask -= np.array([d, 0])
        dst_dsize = (112 - 2*d, 112)

        M, tmp = cv2.estimateAffinePartial2D(src_face_mask, dst_face_mask)

        rows, cols, _ = src_image.shape
        dst_image = cv2.warpAffine(src_image, M, (cols, rows))

        face_img = dst_image[int(bbox[1]):int(bbox[1]+dst_dsize[1]-1), int(bbox[0]):int(bbox[0]+dst_dsize[0]-1)]
    else:
        face_img = src_image[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]

    return face_img

def result2data(frame, yolo_result, score_th: float = -1.0) -> List[LabelData]:
    face_data_list = []
    for res_id, res in enumerate(yolo_result.results):
        face_data = LabelData()
        label = res.setdefault('label', "")
        score = res.setdefault('score', 0.0)
        if label == "face" and score >= score_th:
            bbox = [int(coord) for coord in res.setdefault('bbox', [])]
            if len(bbox) == 4:
                face_data.set_bbox(bbox)
            landmarks = res.setdefault('landmarks', [])
            if len(landmarks) == 5:
                face_data.set_landmarks(landmarks)
            face_data.set_face_score(score)
            face_data.add_property('res_id', res_id)
            face_img = get_face_img(frame, bbox)
            face_data.set_face_image(face_img)
            face_data_list.append(face_data)
    return face_data_list

class DataFaceDoc(threading.Thread):
    """
    Frontend Document:
    - get incoming data,
    - keep them until they are processed in View,
    - publish in the outcoming stream
    """

    def __init__(self, kwargs: dict):
        """
        DataFaceDoc Constructor
        :param q_in: Incoming data queue
        :param config_name: config file name
        """
        super().__init__()

        self.q_in = kwargs.setdefault('q_in', Queue())
        self.q_out_map = kwargs.setdefault('q_out_map', {})
        self.runs_event = kwargs.setdefault('runs_event', multiprocessing.Event())
        config_name = kwargs.setdefault('config', "")

        self.prompt: str = ""
        self.prompt_answer = ""
        self.prompt_result: int = 0

        self.object_id = 0

        # Controlling events
        self.stop_event  = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.clear()

        # Data for processing
        self.face_data: LabelData = None

        # Score Threshold to mark a face as unknown
        self.reject_score_th: float = 0.0
        # Score Threshold to re-check known faces
        self.unsure_score_th: float = 0.0
        # Score Threshold to write known faces
        self.write_score_th: float = 0.0

        # Logging info to be displayed in View
        self.log = ""

        self.vector_searcher = None
        self.vector_writer   = None
        self.dataset_reader  = None

        self.embedder = None

        self.detector_cfg: dict = {}
        self.detect_model = None

        # Load config.
        self.config = ConfigRT(config_name, autostart=False)
        self.apply_config()

    def apply_config(self):
        configs = self.config.get('configs')
        if configs is not None:
            vectordb_cfg = configs.setdefault('vector_db')
            dataset_cfg  = configs.setdefault('dataset_reader')
            embedder_cfg = configs.setdefault('embedder')

            if vectordb_cfg is not None:
                self.vector_searcher = LanceDBSearcher("lancedb_searcher", q_in=None, config_name=vectordb_cfg)
                self.vector_writer = LanceDBWriter("lancedb_writer", q_in=None, config_name=vectordb_cfg)
                self.reject_score_th: float = self.vector_searcher.reject_score_th
                self.unsure_score_th: float = self.vector_searcher.unsure_score_th
                self.write_score_th: float = self.vector_searcher.write_score_th

            if dataset_cfg is not None:
                self.dataset_reader = DatasetSource(config_name=dataset_cfg)
                self.dataset_reader.add_q_out(self.q_in)
                self.dataset_reader.start()

            if embedder_cfg is not None:
                self.embedder = DeepfaceEmbedder("embedder", q_in=None, config_name=embedder_cfg)

        try:
            detector_cfg = self.config.get('detector')
            self.init_detector(detector_cfg)
        except:
            pass

    def init_detector(self, detector_cfg: dict):
        """
        Apply camera-related config
        """
        if detector_cfg != self.detector_cfg:
            cloud_url = detector_cfg.setdefault('cloud_url', "https://cs.degirum.com")
            model_name = detector_cfg.setdefault('model', "yolo_v5s_face_det--512x512_quant_n2x_orca_1")
            image_backend = detector_cfg.setdefault('image_backend', "opencv")
            input_numpy_colorspace = detector_cfg.setdefault('input_numpy_colorspace', 'BGR')

            zoo = dg.connect(dg.CLOUD, cloud_url, mytools.get_token())
            self.detect_model = zoo.load_model(model_name)
            self.detect_model.image_backend = image_backend
            self.detect_model.input_numpy_colorspace = input_numpy_colorspace
            print(f"DataFaceDoc: model {model_name} loaded")

            self.detector_cfg = detector_cfg


    def stop(self):
        print("=========== Stopping Labeller ================")
        if self.dataset_reader is not None:
            self.dataset_reader.stop()
            self.dataset_reader.join()

        if self.vector_searcher is not None:
            self.vector_searcher.stop()  # no need to join, just to stop config
            self.vector_writer.stop()    # no need to join, just to stop config

        self.stop_event.set()
        self.pause_event.set()
        self.join()
        print("=========== Labeller Stopped ================")

    def is_stopped(self):
        return self.stop_event.is_set()

    def run(self):
        self.runs_event.set()
        while not self.is_stopped():
            try:
                data = self.q_in.get(block=True, timeout=1)
                self.process(data)
            except Empty:
                self.log = "Waiting for data to label..."
                continue
            except KeyboardInterrupt as e:
                print("DataFaceDoc: stopping on KeyboardInterrupt" + str(e))
                #self.stop()
            except Exception as e:
                print("Labeller: run: " + str(e))
                continue

    def add_face_data(self, frame):
        if self.embedder is None or self.detect_model is None:
            return
        result = self.detect_model.predict(frame)
        for res in result.results:
            face_data = FaceData()
            label = res.setdefault('label', "")
            score = res.setdefault('score', 0.0)
            if label == "face" and score >= 0.6:
                bbox = [int(coord) for coord in res.setdefault('bbox', [])]
                if len(bbox) == 4:
                    face_data.set_bbox(bbox)
                landmarks = res.setdefault('landmarks', [])
                if len(landmarks) == 5:
                    face_data.set_landmarks(landmarks)
                face_data.set_face_score(score)
                face_img = get_face_img(frame, bbox)
                face_data.set_face_image(face_img)
                embed_data_list = self.embedder.process(face_data)
                if len(embed_data_list) == 0:
                    continue
                label_data = LabelData()
                label_data.from_data(embed_data_list[0])
                self.object_id += 1
                label_data.add_property('object_id', "ext_" + str(self.object_id))
                label_data.add_property('selected', True)
                self.q_in.put_nowait(label_data)

    def process(self, data):
        """
         Make frame_data available for DataFaceView
        """
        if data.get_data_type() == "frame_data":
            frame = data.get_source_image()
            if frame is not None and self.prompt != "":
                self.apply_prompt(frame)
            return

        if self.vector_searcher is not None:
            res = self.vector_searcher.process(data)
            if len(res) > 0:
                data = res[0]

        try:
            score = data.get_score()
        except:
            score = 999.0

        try:
            label = data.get_label()
        except:
            label = ""

        if label.lower() == "unknown" or label == "" or score > self.unsure_score_th:
            # pause until DataFaceView calls publish
            self.log = "Please enter the correct label"
            self.face_data = data
            self.pause_event.clear()
            self.pause_event.wait()
        else:
            self.log = "Known face skipped."

    def publish(self, label_data: LabelData):
        """
        Put processed data in the outbound queue
        """
        if label_data is not None and self.vector_writer is not None:
            self.vector_writer.consume(label_data)

        if 'face_tracker' in self.q_out_map and label_data is not None:
            print("---------------- Sending to Tracker ---------------------")
            self.q_out_map['face_tracker'].put_nowait(label_data)

        self.face_data = None
        self.pause_event.set()

    def apply_prompt(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        prompt, prompt_answer = gemini(mytools.get_google_token(), frame_pil, self.prompt)
        if prompt == self.prompt:
            self.prompt_answer = prompt_answer
            self.prompt_result = 1 if "yes" in self.prompt_answer.lower() else -1
