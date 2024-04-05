import sys
import os

from typing import Dict

sys.path.append(os.getcwd())

from dg_face_tracking.Consumers.consumer import Consumer
from dg_face_tracking.Database.LocalDBAdapter import LocalDBAdapter
from dg_face_tracking.Data.basedata import BaseData
from dg_face_tracking.Data.frame_data import FrameData
from dg_face_tracking.Data.face_data import EmbeddedFaceData

from dg_face_tracking.config_rt import ConfigRT

default_catalogue_path = "C:/Dev/Datasets/SQLite"
default_datasets_path = "C:/Dev/Datasets"

default_config = {
    'src_frames_dataset':
        {
            'catalogue_path': default_catalogue_path,  # path to catalogue (SQLite db)
            'datasets_path': default_datasets_path,    # path to datasets
            'dataset_name': "default_frames",  # dataset name; no data will be saved if empty
            'write_mode': "overwrite",  # write mode. If "overwrite", the dataset will be overwritten
        },
    'new_faces_dataset':
        {
            'catalogue_path': default_catalogue_path,  # path to catalogue (SQLite db)
            'datasets_path': default_datasets_path,  # path to datasets
            'dataset_name': "default_faces",  # dataset name; no data will be saved if empty
            'write_mode': "append",
        }
}


class LocalDBWriter(Consumer):
    """

    """
    def __init__(self, proc_id, q_in, config_name):
        """
        LocalDBWriter constructor
        """
        print("LocalDBAdapter init")

        self.db_adapters: Dict[str, LocalDBAdapter] = {}

        if config_name is None:
            config_name = self.__class__.__name__
        self.config = ConfigRT(config_name)
        try:
            self.apply_config()
        except Exception as e:
            self.config.stop()
            raise e

        super(LocalDBWriter, self).__init__(proc_id, q_in)

    def stop(self):
        """
        Stop adapter
        """
        for db_adapter in self.db_adapters.values():
            db_adapter.stop()
            db_adapter.join()

        super(LocalDBWriter, self).stop()
        print("LocalDBWriter stopped")

    def apply_config(self):
        """
        Try to apply config.
        If failed, but there is a valid configuration setup already, the new one will be ignored
        """
        if not self.config.is_modified():
            return

        cfg = self.config.get("datasets", default_config)
        try:
            self.from_config(cfg)
        except Exception as e:
            raise Exception("CameraSource: apply_config: " + str(e))

    def from_config(self, cfg):
        """
        Apply dataset deployment config
        """
        for dataset_id, dataset_cfg in cfg.items():
            if dataset_id in self.db_adapters:
                db_adapter: LocalDBAdapter = self.db_adapters[dataset_id]
                if db_adapter.is_alive():
                    db_adapter.stop()
                    db_adapter.join()

            catalogue_path = dataset_cfg['catalogue_path']
            datasets_path = dataset_cfg['datasets_path']
            dataset_name = dataset_cfg['dataset_name']
            write_mode = dataset_cfg['write_mode']
            if dataset_name != "":
                try:
                    db_adapter: LocalDBAdapter = LocalDBAdapter(catalogue_path, datasets_path, dataset_name)
                    if write_mode == "overwrite":
                        db_adapter.clear_dataset()
                    db_adapter.start()
                    self.db_adapters[dataset_id] = db_adapter
                except Exception as e:
                    print(f"LocalDBWriter: from_config: Failed to init LocalDBAdapter ({catalogue_path}, {datasets_path}, {dataset_name}): " + str(e))
                print(f"*********** Connected to Dataset  ({catalogue_path}, {datasets_path}, {dataset_name})  ******************")
            # successfully applied cfg

    def consume(self, data: BaseData) -> None:
        """
        data dispatcher
        :param data:  one of BaseData subclasses
        """
        if data.get_data_type() == "frame_data":
            if 'src_frames_dataset' in self.db_adapters:
                db_adapter = self.db_adapters['src_frames_dataset']
                db_adapter.write(data)
            return

        if data.get_data_type() == "label_data":
            if 'new_faces_dataset' in self.db_adapters:
                db_adapter = self.db_adapters['new_faces_dataset']
                db_adapter.write(data)
            return

        raise Exception("LocalDBAdapter: run_query: Unknown query type")

    def _release(self):
        self.config.stop()
        for db_adapter in self.db_adapters.values():
            db_adapter.stop()














