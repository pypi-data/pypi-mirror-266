import sys
import os
import threading
import pickle
import uuid

from typing import List

from queue import Queue

import cv2

import sqlite3

from pathlib import Path
Path(__file__).resolve()

from .DBAdapter import DBAdapter, DBAdapterEmptyException
from ..Data.basedata import BaseData
from ..Data.frame_data import FrameData
from ..Data.face_data import LabelData


class LocalDBAdapter(DBAdapter):
    """
    Adapter to connect to Local dataset deployment
    Blobs are stored as collection of files, one folder for one dataset
    Catalogue is a SQLite database, with a separate table for each dataset
    """
    def __init__(self, catalogue_path, datasets_path, dataset):
        """
        LocalDBAdapter constructor
        :param db_path: path to catalogue (SQLite database)
        :param datasets_path:  path to root of all datasets
        :param dataset: dataset name
        """
        print("LocalDBAdapter init")

        self.dataset = dataset
        self.db_path = catalogue_path

        self.datasets_path = datasets_path
        # path to save datasets (collections of blobs)
        self.files_path = f"{self.datasets_path}/{str(self.dataset)}"
        if not os.path.exists(self.files_path):
            os.mkdir(self.files_path)

        self.db = None          # catalogue connector
        self.db_adapter = None  # access adaptor ()
        self.table = None

        self.prev_time = 0.0

        super(LocalDBAdapter, self).__init__()

    def stop(self):
        """
        Stop adapter
        """
        super(LocalDBAdapter, self).stop()
        print("LocalDBAdapter stopped")

    def disconnect(self) -> None:
        """
        Disconnect from catalogue
        """
        if self.db is not None:
            self.db.close()
            self.db = None
            self.db_adapter = None
            self.table = None

    def release(self) -> None:
        self.disconnect()

    """
    def init_deployment(self,  catalogue_path, datasets_path, dataset, write_mode):

        Apply dataset deployment config

        if write_mode == "overwrite":
            self.clear_dataset()
        if self.db_adapter is not None:
            self.db_adapter.stop()
        if db_adapter is not None:
            db_adapter.start()
        self.db_adapter = db_adapter
    """

    def connect2db(self) -> None:
        """
        Connect to catalogue SQLite DB; check/create a table there; create adapter (cursor) for executing SQL queries
        :param db_path: full path to SQLite db instance
        :param table: table name, should be same as dataset name
        :return: None
        """

        # !!!!! Must be called from the instance's thread !!!!!
        if self.ident is not None and threading.current_thread().ident != self.ident:
            Exception(f"LocalDBAdapter: connect2db: Must be called from the DBAdapter instance's thread")

        # Connect to db. It will be created, if absent
        self.db = sqlite3.connect(self.db_path)

        # Get db cursor (SQLite specific)
        cur = self.db.cursor()

        # Check if dataset_id table is present in db. If not, create it
        check_for_table_sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.dataset}';"
        tables = cur.execute(check_for_table_sql).fetchone()
        if tables is None or self.dataset not in tables:
            cur.execute(f"CREATE TABLE {self.dataset} (data_type, timestamp, frame_uuid, face_uuid, face_name, bbox, location)")
            tables = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.dataset}';").fetchone()
            if tables is None or self.dataset not in tables:
                raise Exception(f"LocalDBAdapter: connect2db: Unable to create {self.dataset} table")

        self.table = self.dataset
        self.db_adapter = cur

    def set_file_path(self, uuid):
        return f"{self.files_path}/{str(uuid)}.jpg"

    def clear_dataset(self) -> None:
        """
        Clear dataset, both in catalogue and all blobs
        """
        try:
            self.connect2db()
            sql = f"DROP TABLE IF EXISTS {self.dataset};"
            self.db_adapter.execute(sql)
            self.db.commit()
            self.disconnect()
        except Exception as e:
            print("LocalDBAdapter: clear_dataset: dropping dataset table: " + str(e))

        try:
            files = os.listdir(self.files_path)
            if files:
                for file in files:
                    file_path = os.path.join(self.files_path, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        except Exception as e:
            print("LocalDBAdapter: clear_dataset: deleting dataset blobs: " + str(e))

    def write(self, data: BaseData) -> None:
        """
        Schedule a data write to dataset
        :param data: FrameData: frame to write
        """
        if data.get_data_type() == "frame_data":
            frame_data: FrameData = data
            query = {"type": "write_frame_data",
                     "path": self.files_path,
                     "frame_data": frame_data}
            self.q.put_nowait(query)

        elif data.get_data_type() == "label_data":
            label_data: LabelData = data
            query = {"type": "write_embedded_face",
                     "path": self.files_path,
                     "label_data": label_data}
            self.q.put_nowait(query)

    def read(self):
        _, frame_data = self.read_frame()
        if frame_data is not None:
            return True, frame_data.get_source_image()
        else:
            return False, None

    def read_frame(self, prev_time: float = -1.0) -> (float, FrameData):
        """
        Read next frame from dataset
        :param prev_time: float:  previous (in dataset) timestamp
        :return: float, FrameData: timestamp and corresponding FrameData
        """
        if self.db_adapter is None:
            self.connect2db()

        if prev_time < 0:
            prev_time = self.prev_time

        frame_data = FrameData()
        sql = f"SELECT * from {self.table} WHERE data_type = 'frame_data' AND timestamp > {prev_time} ORDER BY timestamp ASC LIMIT 1"
        try:
            res = self.db_adapter.execute(sql)
            data_type, next_time, frame_uuid, face_uuid, face_name, bbox, location = res.fetchone()
        except Exception as e:
            raise DBAdapterEmptyException("LocalDBAdapter: read: no more data to read")

        self.prev_time = next_time

        frame_data.set_source_image_uuid(frame_uuid)
        frame_data.set_source_image_time(next_time)

        if not os.path.exists(location+".jpg"):
            return next_time, None

        frame = cv2.imread(location+".jpg")
        frame_data.set_source_image(frame)

        return next_time, frame_data

    def read_labelled_face(self, prev_time: float = -1.0) -> (float, List[LabelData]):
        """
        Read next list of embedded faces from dataset
        :param timestamp: float:  previous (in dataset) timestamp
        :return: time of last read data, list of LabelData
        """
        if self.db_adapter is None:
            self.connect2db()

        if prev_time < 0:
            prev_time = self.prev_time

        label_data_list = []

        sql = f"SELECT * from {self.table} WHERE data_type = 'label_data' AND timestamp > {prev_time} ORDER BY timestamp ASC LIMIT 10"
        try:
            res = self.db_adapter.execute(sql)
            data_type, next_time, frame_uuid, face_uuid, face_name, bbox_str, location = res.fetchone()
        except Exception as e:
            raise DBAdapterEmptyException("LocalDBAdapter: read: no more data to read")

        while True:
            label_data = LabelData()
            label_data.set_source_image_uuid(frame_uuid)
            label_data.set_face_uuid(face_uuid)
            label_data.set_source_image_time(next_time)

            bbox = [int(float(x)) for x in bbox_str.split(',')]
            label_data.set_bbox(bbox)

            label_data.set_label(face_name)

            if os.path.exists(location + ".jpg") and os.path.exists(location + ".emb"):
                face_image = cv2.imread(location+".jpg")
                label_data.set_face_image(face_image)

                with open(location+".emb", 'rb') as f:
                    embeddings = pickle.load(f)
                    label_data.set_embeddings(embeddings)

                label_data_list.append(label_data)

            prev_time = next_time
            try:
                data_type, next_time, frame_uuid, face_uuid, face_name, bbox_str, location = res.fetchone()
                if next_time > prev_time:
                    break
            except:
                break

            self.prev_time = prev_time

        return prev_time, label_data_list if len(label_data_list) > 0 else None

    def _run_query(self, query: dict) -> None:
        """
        Query dispatcher
        :param query:  a dictionary of query parameters
        """
        query_type = query.setdefault('type', "")
        if query_type == "write_frame_data":
            frame_data: FrameData = query['frame_data']
            self.save_data(frame_data)
        elif query_type == "write_embedded_face":
            label_data: LabelData = query['label_data']
            self.save_data(label_data)
        elif query_type == "clear_dataset":
            # erase all dataset data
            dataset = query.setdefault("dataset", "")
            blobs_location = query.setdefault("blobs_location", "")
            self.erase_dataset(dataset, blobs_location)
        elif query_type == "disconnect":
            # disconnect from a catalogue
            self.disconnect()
        else:
            raise Exception("LocalDBAdapter: run_query: Unknown query type")

    def save_data(self, data: BaseData) -> None:
        """
        Save frame_data data to catalogue and to blob storage
        """
        data_type = data.get_data_type()

        image = None
        embeddings = None

        if data_type == "frame_data":
            image = data.get_property('source_image', None)
        elif data_type == "label_data":
            image = data.get_property('face_image', None)
            embeddings = data.get_property('embeddings', None)
        else:
            raise Exception("LocalDBAdapter: save_data: unknown data type")

        if image is None:
            raise Exception("LocalDBAdapter: save_data: missing image")

        timestamp = data.get_property('source_image_time', 0.0)

        frame_uuid = data.get_property('source_image_uuid', "")
        face_uuid = data.get_property('face_uuid', "")
        face_name = data.get_property('label', "")
        bbox = data.get_property('bbox', [0, 0, 0, 0])

        file_uuid = str(uuid.uuid4())
        location = f"{self.files_path}/{file_uuid}"

        bbox_str = ','.join([str(x) for x in bbox])
        sql = f"INSERT INTO {self.table} (data_type, timestamp, frame_uuid, face_uuid, face_name, bbox, location) VALUES ('{data_type}',  {timestamp}, '{frame_uuid}', '{face_uuid}', '{face_name}', '{bbox_str}', '{location}')"
        self.db_adapter.execute(sql)
        self.db.commit()

        if not cv2.imwrite(location + ".jpg", image):
            raise Exception("LocalDBAdapter: save_labelled_face: Failed to write face image")

        if embeddings is not None:
            with open(location + ".emb", 'wb') as f:
                pickle.dump(embeddings, f)














