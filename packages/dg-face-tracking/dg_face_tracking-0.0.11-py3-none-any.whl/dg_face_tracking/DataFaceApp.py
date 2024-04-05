#!/usr/bin/python3

import sys
import os
import argparse

sys.path.append( os.getcwd() )


from Frontend.DataFaceFrontend import run_frontend
from Frontend.DataFaceDoc import DataFaceDoc
from Frontend.DataFaceView import DataFaceView

if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("config")
    try:
        args = argParser.parse_args()
        config_name = args.config
    except:
        config_name = "labelling.cfg"

    params = {
        'Doc': DataFaceDoc,
        'View': DataFaceView,
        'config': config_name,
    }

    run_frontend(params=params)

