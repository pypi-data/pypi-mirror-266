import sys
import os

import numpy as np
from datetime import datetime

from deepface import DeepFace

from pathlib import Path
Path(__file__).resolve()

from ..Process.dg_process import DG_Process
from .processor import Processor, run_processor
from ..Data.face_data import FaceData
from ..Data.face_data import EmbeddedFaceData

default_config = {
    'embedder': {
        'model_name': "VGG-Face",
    }
}

deepface_models = [
  "VGG-Face",
  "Facenet",
  "Facenet512",
  "OpenFace",
  "DeepFace",
  "DeepID",
  "ArcFace",
  "Dlib",
  "SFace",
]

def extract_embeddings(deepface_result):
    embeddings = []
    for res in deepface_result:
        emb = {}
        x1 = res['facial_area']['x']
        y1 = res['facial_area']['y']
        x2 = x1 + res['facial_area']['w']
        y2 = y1 + res['facial_area']['h']
        emb['face_position'] = [x1,y1,x2,y2]
        emb['embedding'] = res['embedding']
        embeddings.append(emb)
    return embeddings


class DeepfaceEmbedderProc(DG_Process):
    def __init__(self, proc_id, q_in, config_name):
        params = {'Processor': DeepfaceEmbedder,
                  'proc_id': proc_id,
                  'q_in': q_in,
                  'config': config_name}
        super(DeepfaceEmbedderProc, self).__init__(proc_id, run_processor, params=params)


class DeepfaceEmbedder(Processor):
    """
    Face image to vector embedding, using Deepface (https://github.com/serengil/deepface)
    """
    def __init__(self, processor_id, q_in, runs_event=None, config_name="DeepfaceEmbedder"):
        print("Deepface_Embedder Processor init")
        self.embedder_cfg: dict = {}
        self.model_name = default_config['embedder']['model_name']
        # Init loading the model
        super(DeepfaceEmbedder, self).__init__(processor_id, q_in, runs_event, config_name)

    def apply_config(self):
        if not self.config.is_modified():
            return

        embedder_cfg = self.config.get('embedder', default_config["embedder"])
        if embedder_cfg != self.embedder_cfg:
            model_name = embedder_cfg.setdefault('model_name', default_config["embedder"]['model_name'])
            if model_name not in deepface_models:
                raise ValueError(f"{model_name} is not a DeepFace model")
            self.model_name = model_name
            self.embedder_cfg = embedder_cfg
            print(f"DeepfaceEmbedder: Applied config for {self.model_name} model.")

    def warm_up(self):
        empty_img = np.zeros((64,64,3), dtype=np.uint8)
        DeepFace.represent(empty_img, model_name=self.model_name, enforce_detection=False)
        super(DeepfaceEmbedder, self).warm_up()


    def process(self, data):
        processed_data = []

        try:
            self.apply_config()
        except Exception as e:
            print("DeepfaceEmbedder: process: Failed to apply config: " + str(e))

        if not isinstance(data, FaceData):
            print("DeepfaceEmbedder: process: data is  not of FaceData type")
            return processed_data

        embedded_face_data = EmbeddedFaceData()
        embedded_face_data.from_data(data)

        start_time = datetime.now()
        face_img = data.get_face_image()
        face_img = face_img.astype(np.float32)
        face_img /= 255.  # needed if detector_backend="skip",
        result = DeepFace.represent(face_img,
                                    model_name=self.model_name,
                                    detector_backend="skip",
                                    enforce_detection=False)

        embeds = result[0]['embedding']
        norm = np.linalg.norm(embeds)
        embeds /= norm

        embedded_face_data.set_embeddings(embeds)
        spent_time = datetime.now() - start_time
        print(f"=================== {self.model_name} embeddings computed. Time spent: {str(int(spent_time.total_seconds() * 1000))}ms")

        embedded_face_data.add_property("destinations", list(self.q_out_map.keys()))
        processed_data.append(embedded_face_data)

        return processed_data

    def stop(self):
        super(DeepfaceEmbedder, self).stop()
        print("Deepface_Embedder Processor stopped")

