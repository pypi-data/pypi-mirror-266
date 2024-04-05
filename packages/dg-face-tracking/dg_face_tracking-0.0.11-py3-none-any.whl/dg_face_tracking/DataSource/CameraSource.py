
import sys
import os
import logging as log

from queue import Queue, Empty
import threading, multiprocessing

import cv2
from typing import Any, Union


from .datasource import DataSource
from ..Data.frame_data import FrameData as FrameData


default_config = {
    'camera': {
        'camera_id': 0,
        'fps_out': 10,
        'show_frames': False,
        'wait_for_empty_queue': False
    }
}


class CameraSource(DataSource):
    def __init__(self, source_id: str = "dataset_source",
                 config_name: str = "",
                 runs_event:  Union[threading.Event, multiprocessing.Event] = None):
        """
        Camera datasource constructor
        :proc_id:
        :param config_path: str: path to config file
        """
        print("CameraSource init")

        # configs
        self.camera_cfg: dict = {}   # camera-related config

        # properties
        self.capture: Any = None  # Camera capture handle
        self.fps_out: int = 0     # Frames rate for output data. If 0 (default), data are output with the rate they are received from camera
        self.lag: float = 0.0     # Time lag between two output frames.

        self.last_timestamp: float = 0.0  # Timestamp, when last frame was sent to output q

        super(CameraSource, self).__init__(source_id, runs_event, config_name)

    @property
    def camera_id(self):
        return self.camera_cfg['camera_id']

    @property
    def show_frames(self):
        return self.camera_cfg['show_frames']

    def apply_config(self):
        """
        Try to apply config.
        If failed, but there is a valid configuration setup already, the new one will be ignored
        """
        q_max_size = self.config.get('q_max_size', -1)
        self.set_q_maxsize(q_max_size)

        camera_cfg = self.config.get('camera', default_config["camera"])
        try:
            self.init_camera(camera_cfg)
        except:
            if self.capture is None:
                raise Exception(f"CameraSource: apply_config: Unable to init camera {camera_cfg['camera_id']}")

    def init_camera(self, camera_cfg: dict):
        """
        Apply camera-related config
        """
        if camera_cfg != self.camera_cfg:
            camera_id = camera_cfg['camera_id']
            if self.capture is None or camera_id != self.camera_id:
                capture = cv2.VideoCapture(camera_id)
                # Check if the video capturing object was initialized correctly
                if not capture.isOpened():
                    raise Exception(f"CameraSource: init: camera {camera_id} cannot be initialized")
                if self.capture is not None:
                    self.capture.release()
                self.capture = capture

            self.fps_out = camera_cfg['fps']
            self.lag = 1.0 / self.fps_out if self.fps_out > 0 else 0.0

            # successfully applied camera_cfg
            self.camera_cfg = camera_cfg
            log.info(f"*********** Applied camera {self.camera_id} config: {self.fps_out} fps **********************")

    def _generate_data(self):
        """
        Implements DataSource abstract method
        - Retrieve frames from camera stream,
        - Pack into FrameData
        - Return FrameData if self.lag time is passed from the sending previous data
        :return: FrameData
        """
        # Capture next frame
        ret, frame = self.capture.read()
        if ret:
            # Create unique FrameData with current timestamp
            frame_data = FrameData()
            frame_data.set_source_image(frame)

            curr_time = frame_data.get_source_image_time()
            # Check if it's time to send frame to output stream
            lag = curr_time - self.last_timestamp
            if lag > self.lag:
                self.last_timestamp = curr_time
                if self.show_frames:
                    # Display the frame to be output
                    cv2.imshow('Video Stream', frame)
                    cv2.waitKey(1)
                return frame_data
            else:
                return None
        else:
            print("No data in camera stream")
            raise Empty


    def stop(self):
        """
        Stop CameraSource service
        """
        # Stop getting new frames
        super(CameraSource, self).stop()

        print("CameraSource stopped")

    def _release(self):
        """
        Release all resources
        """
        # Release camera
        self.capture.release()





