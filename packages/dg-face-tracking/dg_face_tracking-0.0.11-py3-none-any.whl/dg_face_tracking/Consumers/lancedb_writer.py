import sys
import os
from typing import List

import lancedb

sys.path.append( os.getcwd() )

from dg_face_tracking.config_rt import ConfigRT
from dg_face_tracking.Consumers.consumer import Consumer
from dg_face_tracking.Data.face_data import LabelData

default_config = {
    'vectordb': {
        'path': "../db",
        'db_name': "facebase",
        'table_name': "faces"
    }
}

class LanceDBWriter(Consumer):
    """
    LanceDB writer.
    - Receives data from pubsub,
    - checks their validity
    - decides if we need to write them
    - writes to lancedb table
    """
    def __init__(self, proc_id: str, q_in, config_name: str = None):
        """
        LanceDBWriter constructor
        :proc_id: str
        :param q_in: Queue: queue to supply data to be written
        :config_name: str: config filename
        """
        print("LanceDBWriter Consumer init")

        self.vectordb_cfg: dict = {}
        self.db = None
        self.table = None

        if config_name is None:
            config_name = self.__class__.__name__
        self.config = ConfigRT(config_name)
        try:
            self.apply_config()
        except Exception as e:
            self.config.stop()
            raise e

        super(LanceDBWriter, self).__init__(proc_id, q_in)

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
            self.vector_cfg = vectordb_cfg

    def stop(self):
        self.config.stop()
        super(LanceDBWriter, self).stop()
        try:
            table = self.db.open_table(self.table)
            n_rows = table.to_pandas().shape[0]
            print(f"LanceDBWriter: Table {self.table} contains {n_rows}")
        except:
            print(f"LanceDBWriter: Table {self.table} is missing")
        print("LanceDBWriter Consumer stopped")

    def consume(self, label_data: LabelData):
        try:  # try to apply config, if changed
            self.apply_config()
        except FileExistsError as e:
            # Failed to apply updated config, continue with the old one
            print(e)

        data2write = list()
        # TODO: write in batches
        data2write.append( {'image_uuid': label_data.get_source_image_uuid(),
                            'face_uuid': label_data.get_face_uuid(),
                            'face_name': label_data.get_label(),
                            'bbox': label_data.get_bbox(),
                            'vector': label_data.get_embeddings()} )
        try:
            table = self.db.open_table(self.table)
            table.add(data2write)
        except Exception as e:
            try:
                self.db.create_table(self.table, data2write)
            except Exception as e:
                print("LanceDBWriter: consume: Failed to write" + str(e))
                return

        written_names = [d['face_name'] for d in data2write]
        print(f"************** LanceDBWriter: wrote {len(data2write)} faces: {written_names}.")

