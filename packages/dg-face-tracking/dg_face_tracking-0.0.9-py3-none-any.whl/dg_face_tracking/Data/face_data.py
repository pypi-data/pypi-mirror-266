import uuid
from typing import List

from pathlib import Path
Path(__file__).resolve()

from .basedata import BaseData
from .frame_data import FrameData

class FaceData(FrameData):
    def __init__(self) -> None:
        super(FaceData, self).__init__()
        self.set_data_type("face_data")
        self.add_property('face_uuid', str(uuid.uuid4()))

    def copy(self):
        new_data = FaceData()
        new_data.copy_data(self)
        return new_data

    def from_data(self, frame_data: FrameData):
        self.copy_data(frame_data, excluding={'source_image'})

    def set_face_uuid(self, uuid: str):
        self.add_property('face_uuid', uuid)

    def get_face_uuid(self):
        return self.get_property('face_uuid')

    def set_bbox(self, bbox: List[int]):
        self.add_property('bbox', bbox)

    def get_bbox(self):
        return self.get_property('bbox')

    def set_landmarks(self, landmarks):
        self.add_property('landmarks', landmarks)

    def get_landmarks(self):
        return self.get_property('landmarks')

    def set_face_image(self, face_image: List[List[List]]):
        self.add_property('face_image', face_image)

    def get_face_image(self):
        return self.get_property('face_image')

    def set_face_score(self, score: float):
        self.add_property('face_score', score)

    def get_face_score(self):
        return self.get_property('face_score')

class EmbeddedFaceData(FaceData):
    def __init__(self) -> None:
        super(EmbeddedFaceData, self).__init__()
        self.set_data_type("embedded_face_data")

    def copy(self):
        new_data = EmbeddedFaceData()
        new_data.copy_data(self)
        return new_data

    def from_data(self, face_data: FaceData):
        self.copy_data(face_data)

    def set_embeddings(self, embeddings: List[float]):
        self.add_property('embeddings', embeddings)

    def get_embeddings(self):
        return self.get_property('embeddings')


class LabelData(EmbeddedFaceData):
    def __init__(self) -> None:
        super(LabelData, self).__init__()
        self.set_data_type("label_data")
        self.add_property('label', "unknown")
        self.add_property("score", 0.0)

    def copy(self):
        new_data = LabelData()
        new_data.copy_data(self)
        return new_data

    def from_data(self, embedded_face: EmbeddedFaceData):
        self.copy_data(embedded_face)

    def set_label(self, label: str):
        self.add_property('label', label)

    def get_label(self):
        return self.get_property('label')

    def set_score(self, score):
        self.add_property('score', score)

    def get_score(self):
        return self.get_property('score')






