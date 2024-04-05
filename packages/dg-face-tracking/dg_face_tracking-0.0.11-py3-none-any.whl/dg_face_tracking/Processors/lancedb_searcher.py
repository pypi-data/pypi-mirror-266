import sys
import os
from datetime import datetime
from copy import deepcopy
from collections import deque

from typing import List

import lance
import pandas as pd

import lancedb

from pathlib import Path
Path(__file__).resolve()

from ..Processors.processor import Processor
from ..Data.face_data import EmbeddedFaceData, LabelData

default_config = {
    'vectordb': {
        'path': "../db",
        'db_name': "facebase",
        'table_name': "faces"
    },

    'reco_params':{
        # Score Threshold to mark a face as unknown
        'reject_score_th': 0.1,
        # Score Threshold to re-check known faces
        'unsure_score_th': 0.07,
        # Score Threshold to write known faces
        'write_score_th' : 0.06,
        # Unsupervised writing known faces
        'write_known_faces': False
    }
}


class LanceDBSearcher(Processor):
    """
    Searches face embeddings in a vector db
    """
    def __init__(self, processor_id, q_in,  runs_event=None, config_name: str = "LanceDBSearcher"):
        print("LanceDB_Searcher Processor init")
        self.mode = "reco"

        self.vectordb_cfg: dict = {}
        self.db = None
        self.table = None

        self.reco_cfg = {}
        # Score Threshold to mark a face as unknown
        self.reject_score_th: float = default_config['reco_params']['reject_score_th']
        # Score Threshold to re-check known faces
        self.unsure_score_th: float = default_config['reco_params']['unsure_score_th']
        # Score Threshold to write known faces
        self.write_score_th: float = default_config['reco_params']['write_score_th']
        # Unsupervised writing known faces
        self.write_known_faces: bool = default_config['reco_params']['write_known_faces']

        super(LanceDBSearcher, self).__init__(processor_id, q_in, runs_event, config_name)

    def apply_config(self):
        """
        Try to apply config.
        If failed, but there is a valid configuration setup already, the new one will be ignored
        """
        if not self.config.is_modified():
            return

        vectordb_cfg = self.config.get('vectordb', default_config["vectordb"])
        if vectordb_cfg != self.vectordb_cfg:
            path = vectordb_cfg.setdefault('path', default_config["vectordb"]['path'])
            if not os.path.exists(path):
                raise FileExistsError("LanceDBWriter: apply_config: Vector Database path does not exist")

            name = vectordb_cfg.setdefault('db_name', default_config["vectordb"]['db_name'])
            table = vectordb_cfg.setdefault('table_name', default_config["vectordb"]['table_name'])
            full_path = os.path.join(path, name)
            db = lancedb.connect(full_path)
            if db is None:
                raise FileExistsError("LanceDBWriter: apply_config: Cannot connect to Vector Database")

            self.db = db
            self.table = table
            self.vectordb_cfg = vectordb_cfg

        reco_cfg = self.config.get('reco_params', default_config["reco_params"])
        if reco_cfg != self.reco_cfg:
            self.reject_score_th = reco_cfg.setdefault('reject_score_th', default_config["reco_params"]['reject_score_th'])
            self.unsure_score_th = reco_cfg.setdefault('unsure_score_th', default_config["reco_params"]['unsure_score_th'])
            self.write_score_th = reco_cfg.setdefault('write_score_th', default_config["reco_params"]['write_score_th'])
            self.write_known_faces = reco_cfg.setdefault('write_known_faces', default_config["reco_params"]['write_known_faces'])

    def stop(self):
        super(LanceDBSearcher, self).stop()
        print("LanceDB_Searcher Processor stopped")

    def num_rows(self) -> int:
        """
        Return number of records in lancedb table
        """
        try:
            table = self.db.open_table(self.table)
            return table.to_pandas().shape[0]
        except Exception as e:
            return 0

    def process(self, embedded_face):
        try:
            self.apply_config()
        except FileExistsError as e:
            print("LanceDBSearcher: process: Failed to apply config: " + str(e))

        processed_data = []

        # data must come either from embedder, or from new faces dataset
        if not isinstance(embedded_face, EmbeddedFaceData) and not isinstance(embedded_face, LabelData):
            print("LanceDBSearcher: process: data is  not of EmbeddedFaceData type")
            return processed_data

        label_data = LabelData()
        label_data.from_data(embedded_face)

        start_time = datetime.now()
        embeddings = embedded_face.get_embeddings()
        if embeddings is None:
            print("LanceDBSearcher: process: Missed embeddings!!!")
            return processed_data

        face_uuid, face_name, score = self.face_search(embeddings=embeddings)
        label_data.set_score(score)
        if score < self.reject_score_th:
            label_data.set_face_uuid(face_uuid)
            label_data.set_label(face_name)

        spent_time = datetime.now() - start_time

        print(f"LanceDB_Searcher: Face of: {face_name}. Distance: {score}.  Time spent: {str(int(spent_time.total_seconds() * 1000))}ms")

        destinations = self.where2send(score)
        label_data.add_property("destinations", destinations)

        processed_data.append(label_data)
        return processed_data

    def face_search(self, embeddings: List[float]):
        """
        Search face by embedding
        """
        default = ("", "unknown", 999.9)

        if len(embeddings) == 0:
            raise Exception("LanceDBSearcher: face_search: no embeddings")

        try:
            table = self.db.open_table(self.table)
        except:
            return default

        df = table.search(embeddings).metric("cosine").limit(10).to_df()
        # df.to_pickle("df.pkl")

        # Best matches for each face_uuid
        best_matches_df = df[ df.groupby('face_uuid')['_distance'].transform(min) == df['_distance'] ]
        best_matches_df = best_matches_df.sort_values(by=['_distance'], ascending=True)

        face_uuid = best_matches_df.iloc[0].face_uuid
        face_name = best_matches_df.iloc[0].face_name
        score     = best_matches_df.iloc[0]._distance

        # For now, return only the best match
        return face_uuid, face_name, score

    def where2send(self, score):
        destinations = []

        # if score < self.unsure_score_th:
        # send to face_detector anyway
        destinations.append("face_tracker")   # destinations.append("face_detector")

        if score > self.unsure_score_th:
            destinations.append("dataset_writer")

        # TODO: Do we need unsupervised update?
        if self.write_known_faces and self.write_score_th <= score < self.unsure_score_th:
            destinations.append("vector_writer")

        return destinations





