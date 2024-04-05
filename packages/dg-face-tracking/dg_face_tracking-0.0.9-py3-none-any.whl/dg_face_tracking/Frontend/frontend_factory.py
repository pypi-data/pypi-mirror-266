from pathlib import Path
Path(__file__).resolve()

from .DataFaceFrontend import DataFaceFrontend

def create_frontend(frontend_id, config):
    if frontend_id == 'labeller':
        return [DataFaceFrontend(config)]

    raise Exception(f"create_frontend: {frontend_id}: No such Frontend")


