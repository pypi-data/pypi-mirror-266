from pathlib import Path
Path(__file__).resolve()

from .face_detector import FaceDetector
from .face_embedder import FaceEmbedder
from .lancedb_searcher  import LanceDBSearcher


def create_data_processor(proc_id, config_name, q_in=None, n_process=0):
    """
    if proc_id == "deepface_embedder":
        if n_process == 0:
            return [DeepfaceEmbedder("face_embedder", q_in, config_name)]
        else:
            # params = {'Processor': DeepfaceEmbedder, 'q_in': q_in, 'config': config_name}
            # super(DeepfaceEmbedderProc, self).__init__(proc_id, run_processor, params=params)
            return [DeepfaceEmbedderProc("face_embedder", q_in, config_name) for _ in range(n_process)]
    """
    if proc_id == "lancedb_searcher":
        return [LanceDBSearcher("vector_searcher", q_in, config_name=config_name)]
    if proc_id == "face_detector":
        return [FaceDetector("face_detector",  config_name=config_name, q_in=q_in)]
    if proc_id == "face_embedder":
        return [FaceEmbedder("face_embedder",  config_name=config_name, q_in=q_in)]
    else:
        raise Exception(f"{proc_id}: No such Processor")


