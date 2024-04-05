import sys
import os

import threading, multiprocessing

from datetime import datetime
from typing import Any, Union

from pathlib import Path
Path(__file__).resolve()

from .datasource import DataSource
from ..Database.LocalDBAdapter import LocalDBAdapter


default_config = {
    'camera_emulator': {
        'fps_out': 10,
        'show_frames': False
    },
    'dataset':
    {
        'catalogue_path': "C:/Dev/Datasets/SQLite",
        'dataset_path': "C:/Dev/Datasets",
        'dataset_name': "test_dataset",
    }
}

class DatasetSource(DataSource):
    def __init__(self, source_id: str = "camera_source",
                 config_name: str = "",
                 runs_event:  Union[threading.Event, multiprocessing.Event] = None):
        """
        Camera datasource constructor
        :param q_out: Queue: outgoing data stream
        """
        print("DatasetSource init")

        self.content = ""   # what kind of data are in the dataset

        self.emulator_cfg: dict = {}   # camera emulator config
        self.dataset_cfg: dict = {}  # dataset deployment config

        # properties
        self.fps_out: int = 0     # Frames rate for output data. If 0 (default), data are output with the rate they are received from camera
        self.lag: float = 0.0     # Time lag between two output frames.

        self.n_frames: int = 0  # number of frames read

        self.last_timestamp: float = 0.0          # timestamp when the last frame was generated
        self.prev_dataset_timestamp: float = 0.0  # timestamp of the last frame retrieved from dataset

        self.db_adapter: Any = None
        super(DatasetSource, self).__init__(source_id, runs_event, config_name)

    @property
    def camera_id(self):
        return self.emulator_cfg['camera_id']

    @property
    def show_frames(self):
        return self.emulator_cfg['show_frames']

    @property
    def deployment(self):
        return self.dataset_cfg['deployment']
    @property
    def dataset(self):
        return self.dataset_cfg['dataset_name']

    def apply_config(self):
        """
        Try to apply config.
        If failed, but there is a valid configuration setup already, the new one will be ignored
        """
        keep_running = self.config.get('keep_running', False)
        self.set_keep_running(keep_running)

        q_maxsize = self.config.get('queue_maxsize', -1)
        self.set_q_maxsize(q_maxsize)

        emulator_cfg = self.config.get('camera_emulator', default_config["camera_emulator"])
        try:
            self.init_emulator(emulator_cfg)
        except:
            raise Exception(f"DatasetSource: apply_config: Unable to init camera emulator")

        dataset_cfg = self.config.get("dataset", default_config["dataset"])
        try:
            self.init_dataset(dataset_cfg)
        except:
            if len(dataset_cfg['dataset_name']) != 0 and self.db_adapter is None:
                # We want to use some dataset, but for some reason have no adapter to it
                raise Exception(f"DatasetSource: apply_config: Unable to init dataset adapter for  {dataset_cfg['dataset_name']}")

    def init_emulator(self, emulator_cfg):
        """
        Apply emulator-related config
        """
        if emulator_cfg != self.emulator_cfg:
            if 'fps_out' in emulator_cfg:
                self.fps_out = emulator_cfg['fps_out']
                self.lag = 1.0 / self.fps_out if self.fps_out > 0 else 0.0
            else:
                self.fps_out = 0.0
                self.lag = 0.0

                # successfully applied emulator_cfg
            self.emulator_cfg = emulator_cfg
            print(f"*********** Applied camera emulator config at {self.fps_out} fps **********************")

    def init_dataset(self, dataset_cfg):
        """
        Apply dataset deployment config
        """
        if dataset_cfg != self.dataset_cfg:
            self.content = dataset_cfg['content']
            if len(dataset_cfg['dataset_name']) != 0:
                db_adapter = LocalDBAdapter(catalogue_path=dataset_cfg['catalogue_path'],
                                            datasets_path=dataset_cfg['datasets_path'],
                                            dataset=dataset_cfg['dataset_name'])
                self.db_adapter = db_adapter
            else:
                # No dataset is requested in config
                if self.db_adapter is not None:
                    # self.db_adapter.stop()
                    self.db_adapter = None
            # successfully applied deployment_cfg
            self.dataset_cfg = dataset_cfg
            print(f"*********** Applied {self.deployment} deployment, dataset {self.dataset}  ******************")

    def _generate_data(self):
        """
        Implements DataSource abstract method
        - Retrieve Data from dataset  with a given time lag
        :return: FrameData or LabelData
        """
        # apply config changes, if any
        self.apply_config()
        # Check if it's time to send frame to output stream
        curr_timestamp = datetime.now().timestamp()
        lag = curr_timestamp - self.last_timestamp
        if lag < self.lag:
            return None

        data = None
        self.last_timestamp = curr_timestamp
        if self.content == "frames":
            # Read FrameData from dataset
            timestamp, frame_data = self.db_adapter.read_frame(self.prev_dataset_timestamp)
            self.prev_dataset_timestamp = timestamp
            if frame_data is not None and frame_data.get_source_image() is not None:
                frame_data.add_property('destinations', ['face_detector'])
                self.n_frames += 1
                data = frame_data
        elif self.content == "faces":
            timestamp, label_data_list = self.db_adapter.read_labelled_face(self.prev_dataset_timestamp)
            self.prev_dataset_timestamp = timestamp
            if label_data_list is not None:
                for label_data in label_data_list:
                    label_data.add_property('destinations', ['frontend'])
                    self.n_frames += 1
                data = label_data_list
        else:
            data = None

        return data

    def stop(self):
        """
        Stop DatasetSource service
        """
        # Stop db adapter
        if self.db_adapter.is_alive():
            self.db_adapter.stop()
            self.db_adapter.join()

        self.config.stop()

        super(DatasetSource, self).stop()
        print("DatasetSource stopped")

    def _release(self):
        """
        Release all resources
        """
        self.config.stop()
        print(f"DatasetSource: Total number of frames read: {self.n_frames}")





