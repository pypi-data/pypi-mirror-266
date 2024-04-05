from pathlib import Path
Path(__file__).resolve()

from ._version import __version__, __version_info__
from .track_faces import track_faces


def _command_entrypoint(arg_str=None):
    track_faces()

