import argparse
import os, sys

from pathlib import Path
Path(__file__).resolve()

from .face_tracker_controller import FaceTrackerController


def track_faces():
    default_deployment = "docker"
    default_config_name = ""
    default_command = ""

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config",
                           help="main config file path",
                           default=default_config_name)
    parser.add_argument("-d", "--deployment",
                           choices=["cloud","local", "docker"],
                           help="deployment type: cloud or local",
                           default=default_deployment)
    parser.add_argument("-e", "--exec",
                           help="execute service command",
                           choices=["delete_embeds"],
                           default=default_config_name)
    command = default_command
    try:
        args = parser.parse_args()
        config_name = args.config
        deployment = args.deployment
        command = args.exec
    except Exception as e:
        pass

    if command == "delete_embeds":
        if os.path.isfile("embeds.db"):
            os.remove("embeds.db")

    try:
        ft = FaceTrackerController(deployment, config_name)
        ft.run()
    except:
        print("DataFace: main: Failed to Config controller")


if __name__ == "__main__":
    track_faces()