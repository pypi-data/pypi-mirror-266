import sys, os
import threading
import multiprocessing
from queue import Queue, Empty as EmptyQueue

import numpy as np
import cv2

from typing import Optional, Union

from validators import ipv4, url

import degirum as dg
import time

from pathlib import Path
Path(__file__).resolve()

import degirum_tools
from ..config_rt import ConfigRT

from ..Data.face_data import FaceData
from ..Data.face_data import EmbeddedFaceData

default_config = {
    'model': {
        'cloud_url': "https://cs.degirum.com/degirum/Barkas",
        'model': "facenet--160x160_float_trt_gpu_1",
        'input_image_format': "RAW",
        'input_numpy_colorspace': "RGB",
        'input_letterbox_fill_color': [114, 114, 114]
    }
}

def is_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True


class FaceEmbedder(threading.Thread):
    def __init__(self, proc_id: str = "face_embedder",
                 config_name: str = "FaceEmbedder",
                 q_in: Union[Queue, multiprocessing.Queue] = None,
                 runs_event:  Union[threading.Event, multiprocessing.Event] = None):
        self.proc_id = proc_id
        self.q_in = Queue() if q_in is None else q_in
        self.q_out_map: dict = {}

        self.stop_event = threading.Event()
        self.runs_event = threading.Event() if runs_event is None else runs_event

        self.results_thread = threading.Thread(target=self.process_results, args=())
        self.result_queue = Queue()

        self.deployment = os.environ['DG_DEPLOYMENT']
        self.cloud_token = degirum_tools.get_token() if self.deployment.lower() == "cloud" else ""

        self.show_faces = False
        self.flip_face = False

        self.model = None
        self.model_cfg: dict = {}

        self.n_total_embeds = 0
        self.start_time = -1

        self.n_try = 5

        # Starting real-time config tracking service
        if config_name is None:
            config_name = self.__class__.__name__
        try:
            self.config = ConfigRT(config_name)
            self.apply_config()
        except Exception as e:
            self.config.stop()
            raise e

        super(FaceEmbedder, self).__init__()

    def stop(self):
        self.config.stop()
        self.stop_event.set()
        self.results_thread.join()

    def is_stopped(self) -> bool:
        """
        Check if the service is stopped
        :return: bool
        """
        return self.stop_event.is_set()

    def wait2run(self):
        self.runs_event.wait()

    def add_q_out(self, destination, q_out):
        self.q_out_map[destination] = q_out

    def start(self) -> None:
        self.results_thread.start()
        super(FaceEmbedder, self).start()

    def get_id(self):
        """
        Returns source id
        :return: str
        """
        return self.proc_id

    def apply_config(self):
        if not self.config.is_modified():
            return

        self.show_faces = self.config.get('show_faces', False)
        self.flip_face = self.config.get('flip_face', False)

        try:
            model_cfg = self.config.get('model', default_config['model'])
            if model_cfg != self.model_cfg:
                cloud_url = model_cfg.setdefault('cloud_url', "")
                model_name = model_cfg['model']
                local_zoo_path = model_cfg.setdefault('local_zoo_path', "")

                if "cloud" in self.deployment:
                    zoo = dg.connect(dg.CLOUD, cloud_url, self.cloud_token)
                elif "local" in self.deployment:
                    model_path = os.path.join(local_zoo_path, model_name, model_name + '.json')
                    zoo = dg.connect(dg.LOCAL, model_path)
                elif ipv4(self.deployment):
                    zoo = dg.connect(self.deployment)
                elif "docker" in self.deployment:
                    zoo = dg.connect("127.0.0.1")
                else:
                    raise Exception(f"FaceTracker Demo: init_detector: unknown deployment: {self.deployment}")

                model = zoo.load_model(model_name)
                model.input_image_format = model_cfg['input_image_format']
                input_letterbox_fill_color = model_cfg.setdefault('input_letterbox_fill_color', [114, 114, 114])
                model.input_letterbox_fill_color = tuple(input_letterbox_fill_color)
                model.input_numpy_colorspace = model_cfg.setdefault('input_numpy_colorspace', "BGR")
                model.input_pad_method = model_cfg.setdefault('input_pad_method', "letterbox")
                # model.save_model_image = True
                self.model = model
                self.model_cfg = model_cfg
                print(f"FaceEmbedder: Applied config for {model_name} model.")
        except Exception as e:
            print("FaceEmbedder: apply_config: " + str(e))
            raise e

    def put2q(self, data):
        for q_out in self.q_out_map.values():
            try:
                q_out.put_nowait(data)
            except Exception as e:
                print("FaceEmbedder: result_process: failed to put in q_out" + str(e))

    def run(self):
        self.runs_event.set()
        while not self.stop_event.is_set():
            try:
                for res in self.model.predict_batch(self.data_source()):
                    self.result_queue.put(res)
                self.result_queue.put_nowait(None)
                break
            except Exception as e:
                print("FaceEmbedder: run: " + str(e))
        # Stop result_process thread
        self.result_queue.put(None)
        self.results_thread.join()
        self.config.stop()
        spent_time = time.time() - self.start_time
        print(
            f"FaceEmbedder: Total embeddings: {self.n_total_embeds}; Throughput: {self.n_total_embeds / spent_time:.1f} embeddings per second")
        print("FaceEmbedder: exiting")

    def test_data_source(self):
        self.start_time = time.time()
        for _ in range(1000):
            face_img = np.zeros((160, 160, 3))
            yield face_img, FaceData()
            time.sleep(0.01)

    def data_source(self):
        flipped = False
        flipped_img = None
        prev_data = None

        while not self.is_stopped():
            if not flipped:
                try:
                    data = self.q_in.get(timeout=0.1)
                    if self.start_time < 0:
                        self.start_time = time.time()
                except:
                    continue

                if data is None:
                    print("FaceEmbedder: Got poison pill")
                    break
                if isinstance(data, FaceData):
                    face_img = data.get_face_image()
                    if self.show_faces:
                        cv2.imshow("faces", face_img)
                        cv2.waitKey(1)
                        time.sleep(1)

                    if self.flip_face:
                        flipped_img = cv2.flip(face_img, 1)
                        prev_data = data
                        flipped = True
                    yield face_img, data
            else:
                flipped = False
                yield flipped_img, prev_data

    def process_results(self):
        flipped = False
        prev_embeds = None
        prev_data = None

        while not self.is_stopped():
            try:
                result = self.result_queue.get(timeout=0.1)
            except:
                continue
            if result is None:
                print("FaceEmbedder: Added poison pill")
                self.put2q(None)
                break
            if len(result.results) == 0 or 'data' not in result.results[0]:
                continue

            embeds = result.results[0]['data'].flatten()
            face_data = result.info

            self.n_total_embeds += 1
            # print( f"FaceEmbedder: process_results: got embedding {self.n_total_embeds}")

            if self.flip_face:
                if prev_embeds is None:
                    prev_embeds = embeds
                    prev_data = face_data
                    continue
                else:
                    if prev_data == face_data:
                        embeds += prev_embeds
                        prev_embeds = None
                        prev_data = None
                    else:
                        print("FaceEmbedder: process_results: wrong flipped data")

            norm = np.linalg.norm(embeds)
            embeds /= norm

            embedded_face = EmbeddedFaceData()
            embedded_face.from_data(face_data)
            embedded_face.set_embeddings(list(embeds))

            self.put2q(embedded_face)
        # end of while
        return

