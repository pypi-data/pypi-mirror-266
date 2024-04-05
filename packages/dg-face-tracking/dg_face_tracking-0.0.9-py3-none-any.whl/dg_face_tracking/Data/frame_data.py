from datetime import datetime
import uuid
from typing import List

from pathlib import Path
Path(__file__).resolve()

from .basedata import BaseData

class FrameData(BaseData):
    def __init__(self) -> None:
        super(FrameData, self).__init__()
        self.set_data_type("frame_data")
        self.add_property('source_image_uuid', str(uuid.uuid4()))
        self.add_property('source_image_time', datetime.now().timestamp())

    def copy(self):
        new_data = FrameData()
        new_data.copy_data(self)
        return new_data

    def set_source_image(self, frame):
        self.add_property("source_image", frame)

    def get_source_image(self):
        return self.get_property("source_image")

    def set_source_image_time(self, t):
        self.add_property('source_image_time', t)

    def get_source_image_time(self):
        return self.get_property('source_image_time')

    def set_source_image_uuid(self, uuid):
        self.add_property('source_image_uuid', uuid)

    def get_source_image_uuid(self):
        return self.get_property('source_image_uuid')

    def get_cropped_image(self, bbox: List[int]):
        frame = self.get_source_image()
        return frame[bbox[1]:bbox[3], bbox[0]:bbox[2]]

    def __lt__(self, other):
        return self.get_source_image_time() < other.get_source_image_time()

    def __gt__(self, other):
        return self.get_source_image_time() > other.get_source_image_time()

    def __le__(self, other):
        return self.get_source_image_time() <= other.get_source_image_time()

    def __ge__(self, other):
        return self.get_source_image_time() >= other.get_source_image_time()