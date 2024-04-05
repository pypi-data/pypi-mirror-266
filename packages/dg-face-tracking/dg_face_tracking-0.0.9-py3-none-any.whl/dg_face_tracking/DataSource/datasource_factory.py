from pathlib import Path
Path(__file__).resolve()

from .CameraSource import CameraSource
from .FolderSource import FolderSource
from .DatasetSource import DatasetSource
from .face_tracker import FaceTracker
from .face_tracker_demo import FaceTrackerDemo


def create_data_source(source_id: str, q_in, source_cfg):
    if source_id == "face_tracker":
        return FaceTracker(q_in, source_cfg)
    if source_id == "face_tracker_demo":
        return FaceTrackerDemo(q_in, source_cfg)
    if source_id == "folder_source":
        return FolderSource(q_in, source_cfg)
    if source_id == "camera":
        return CameraSource(source_id=source_id, config_name=source_cfg)
    elif source_id == "dataset":
        return DatasetSource()
    else:
        raise Exception(f"create_data_source: No {source_id} DataSource")