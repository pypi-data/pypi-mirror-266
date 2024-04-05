import sys
import os

import numpy
import numpy as np
from datetime import datetime
from collections import defaultdict, deque
from typing import List, Any, Hashable

import uuid

from pathlib import Path
Path(__file__).resolve()
from ..norfair.tracker import  Detection

from ..Data.face_data import FaceData, LabelData


class TrackedObject:
    """
    TrackedObject Class.
    Holds info about a particular object.
    """
    def __init__(self):
        self.label: str = "Unknown"
        self.id = str(uuid.uuid4())
        self.start_time: float = -1.0
        self.last_time: float = -1.0
        self.track = deque()
        self.lookup = defaultdict(np.ndarray)

    @property
    def get_global_id(self):
        return self.id

    def update(self, timestamp: float, frame_uuid: str, points: np.ndarray, max_lag: float):
        self.last_time = timestamp
        self.track.append((timestamp, frame_uuid, points))
        self.lookup[frame_uuid] = points

        if self.start_time < 0:
            self.start_time = timestamp

        while timestamp - self.start_time > max_lag:
            t, frame_uuid, _ = self.track.popleft()
            del self.lookup[frame_uuid]
            self.start_time, _, _ = self.track[0]

    def predict(self, frame_uuid=None):
        if frame_uuid is not None and frame_uuid in self.lookup:
            return self.lookup[frame_uuid]

        if len(self.track) > 0:
            _, _, points = self.track[-1]
            return points

        return None

    @property
    def estimate(self) -> np.ndarray:
        """Get the position estimate of the object from the Kalman filter.

        Returns
        -------
        np.ndarray
            An array of shape (self.num_points, self.dim_points) containing the position estimate of the object on each axis.
        """
        return self.get_estimate()

    def get_estimate(self, absolute=False) -> np.ndarray:
        positions = self.predict()  # TODO: implement extrapolation
        return positions


class Tracker:
    """
    Tracker Class.
    Tracks objects in time, predicts their position, re-id objects according new data
    """
    def __init__(self):
        self.max_lag = 20.0  # tracking timeframe
        self.tracked_objects = defaultdict(TrackedObject)

    def re_id(self, detection: Detection):
        try:
            object_id = detection.object_id
            reid_obj = self.tracked_objects[object_id]
        except:
            reid_obj = self.get_best_object(detection.points, detection.source_id)

        if reid_obj is None:
            return

        other_obj = None
        for obj in self.tracked_objects.values():
            if obj.object_id == detection.object_id:
                other_obj = obj

        reid_obj.label = detection.label
        if reid_obj.id != detection.object_id:
            del self.tracked_objects[reid_obj.object_id]
            self.tracked_objects[detection.object_id] = reid_obj
            reid_obj.object_id = detection.object_id

        if other_obj is not None and other_obj != reid_obj:
            other_obj.label = "unknown"
            other_obj.object_id = ""


    def update(self, detections: List[Detection]) -> List[TrackedObject]:  # timestamp, frame_uuid, dg_face_data: List[Dict]):
        for d in detections:
            obj = self.get_best_object(d.points)
            if obj is None:
                obj = TrackedObject()
                self.tracked_objects[obj.id] = obj

            obj.update(d.timestamp, d.source_id, d.points, self.max_lag)

        return list(self.tracked_objects.values())

    def get_best_object(self, points, frame_uuid=None):
        TH = 300
        best_object = None
        best_dist = 111111111
        for obj in self.tracked_objects.values():
            obj_points = obj.predict(frame_uuid)
            if obj_points is not None:
                diff = obj_points.flatten() - points.flatten()
                dist = np.dot(diff.T, diff)
                if best_dist > dist and dist < TH:
                    best_dist = dist
                    best_object = obj

        return best_object

