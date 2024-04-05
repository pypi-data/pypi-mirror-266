import sys
import os

import threading, multiprocessing
import time
from queue import Empty
import pickle
import math
import re

from datetime import datetime
from typing import Any, Union, Tuple

import numpy as np
import cv2

from sklearn.datasets import fetch_lfw_pairs

from pathlib import Path
Path(__file__).resolve()

from ..DataSource.datasource import DataSource
from ..Data.frame_data import FrameData
from ..Data.face_data import FaceData

default_config = {
    'camera_emulator': {
        'fps_out': 10,
        'show_frames': False
    },
    'dataset':
    {
        'catalogue_path': "C:/Dev/Datasets/SQLite",
        'dataset_path': "C:/Dev/Datasets",
        'dataset_name': "test_dataset",
    }
}


def rotation(image, angleInDegrees):
    h, w = image.shape[:2]
    img_c = (w / 2, h / 2)

    rot = cv2.getRotationMatrix2D(img_c, angleInDegrees, 1)

    rad = math.radians(angleInDegrees)
    sin = math.sin(rad)
    cos = math.cos(rad)
    b_w = int((h * abs(sin)) + (w * abs(cos)))
    b_h = int((h * abs(cos)) + (w * abs(sin)))

    t1 = h * abs(sin)

    rot[0, 2] += ((b_w / 2) - img_c[0])
    rot[1, 2] += ((b_h / 2) - img_c[1])

    tmpImg = cv2.warpAffine(image, rot, (b_w, b_h), flags=cv2.INTER_LINEAR)

    tmp_h, tmp_w, _ = tmpImg.shape
    margin_y = (tmp_h - h) // 2
    margin_x = (tmp_w - w) // 2

    outImg = tmpImg[margin_y : margin_y + h, margin_x : margin_x + w]

    return outImg


def create_lfw_name(originals_path, person, t):
    fname = person + '_' + '0'*(4-len(t)) + t + '.jpg'
    return os.path.join(originals_path, person, fname)


def pairs_file_generator(originals_path, pairs_path):
    print(f"Starting pairs_file_generator in {os.getcwd()}")
    start_time = time.time()
    n_data = 0
    if not os.path.isdir(originals_path):
        print(f"FolderSource: pairs_file_generator: {originals_path} does not exists.")
        return
    if not os.path.isfile(pairs_path):
        print(f"FolderSource: pairs_file_generator: {pairs_path} does not exists.")
        return

    with open(pairs_path, 'r') as file:
        idx = -1
        while True:
            idx += 1
            line = file.readline()
            if line == "":
                break
            tokens = line.rstrip().split("\t")
            if len(tokens) == 3:
                target = 1
                person = tokens[0]
                for t in tokens[1:3]:
                    fname = create_lfw_name(originals_path, person, t)
                    if not os.path.isfile(fname):
                       print(f"FolderSource: pairs_file_generator: {fname} does not exists.")
                       break
                    img = cv2.imread(fname)
                    data = FrameData()
                    data.set_source_image(img)
                    data.add_property('source_file', fname)
                    data.add_property('target', target)
                    data.add_property('pair_idx', idx)
                    n_data += 1
                    yield data

            elif len(tokens) == 4:
                target = 0
                for i in range(1,4,2):
                    person = tokens[i-1]
                    t = tokens[i]
                    fname = create_lfw_name(originals_path, person, t)
                    if not os.path.isfile(fname):
                        print(f"FolderSource: pairs_file_generator: {fname} does not exists.")
                        break
                    img = cv2.imread(fname)
                    data = FrameData()
                    data.set_source_image(img)
                    data.add_property('source_file', fname)
                    data.add_property('target', target)
                    data.add_property('pair_idx', idx)
                    n_data += 1
                    yield data
            elif len(tokens) == 0:
                break
            else:
                print(f"FolderSource: pairs_file_generator: wrong data: {tokens}")
                continue
    elapsed = time.time() - start_time
    print(f"Pairs_file_generator finished: {n_data} data points; {n_data / elapsed:.2f} per second")
    yield None

def save_img(img, subset, pair_idx, idx_in_pair, target):
    fname = f"C:/Datasets/lfw_pairs/{subset}/{pair_idx}_{idx_in_pair}_{target}.png"
    cv2.imwrite(fname, img)

def sklearn_file_generator(subset: str):
    print(f"Starting fetch_lfw_pairs generator, subset: {subset}")
    lfw_pairs = fetch_lfw_pairs(subset=subset, color=True, resize=1)
    pairs = lfw_pairs['pairs']
    targets = lfw_pairs['target']
    for idx, pair in enumerate(pairs):
        target = targets[idx]
        idx_in_pair = 1
        for img in pair:
            img *= 255.0
            img = img.astype(np.uint8)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            data = FaceData()
            data.set_face_image(img)
            data.add_property('pair_idx', idx)
            data.add_property('target', target)
            save_img(img, subset, idx, idx_in_pair, target)
            idx_in_pair += 1
            yield data
    yield None


def bin_file_generator(path):
    if not os.path.isfile(path):
        print(f"FolderSource: bin_file_generator: {path} does not exists.")
        return

    try:
        with open(path, 'rb') as file:
            bins, issame = pickle.load(file)  # Python 2 compatibility
    except UnicodeDecodeError:
        with open(path, 'rb') as file:
            bins, issame = pickle.load(file, encoding='bytes')  # Python 3 compatibility

    image_size = 0
    bin_idx = 0
    for idx in range(len(issame)):
        target = 1 if issame[idx] else 0
        for i in range(2):
            _bin = bins[bin_idx]
            bin_idx += 1
            img = cv2.imdecode(np.frombuffer(_bin, np.uint8), cv2.IMREAD_COLOR)
            if image_size == 0:
                image_size = img.shape[0]
            if img.shape[0] != image_size or img.shape[1] != image_size:
                img = cv2.resize(img, (image_size, image_size))
            data = FaceData()
            data.set_face_image(img)
            data.add_property('pair_idx', idx)
            data.add_property('target', target)
            yield data
    yield None


def img_file_generator(folder):
    face_id = -1
    for d in os.listdir(folder):
        label = d
        face_id += 1
        d = os.path.join(folder, d)
        if os.path.isdir(d):
            for f in os.listdir(d):
                f = os.path.join(d, f)
                if os.path.isfile(f):
                    f1, ext = os.path.splitext(f)
                    f1, name = os.path.split(f1)
                    _, label = os.path.split(f1)
                    if ext in [".jpg", ".jpeg", ".png"]:
                        img = cv2.imread(f)
                        data = FrameData()
                        data.set_source_image(img)
                        data.add_property('source_file', f)
                        data.add_property('face_id', face_id)
                        data.add_property('label', label)
                        yield data
    yield None

class FolderSource(DataSource):
    def __init__(self, source_id: str = "folder_source",
                 config_name: str = "",
                 runs_event:  Union[threading.Event, multiprocessing.Event] = None):
        """
        Camera datasource constructor
        :param q_out: Queue: outgoing data stream
        """
        print("FolderSource init")

        self.source = "folder"

        self.folder = None   # where images are residing, one class per subfolder
        self.bin_file = None
        self.show_image = False
        self.subset = None

        self.cnt_frames = 0
        self.max_frames = -1

        self.rotation_angle = 0   # degrees
        self.margin_x = 0
        self.margin_y = 0

        self.img_generator = None
        super(FolderSource, self).__init__(source_id, runs_event, config_name)

    def apply_config(self):
        """
        Try to apply config.
        """
        source = self.config.get('source', "folder")
        if source not in ["folder", "bin", "sklearn", "pairs"]:
            raise Exception(f"FolderSource: apply_config: source {source} does not exist.")
        self.source = source
        if self.source == "sklearn":
            sklearn_cfg = self.config.get('sklearn', {'subset': 'train'})
            self.subset = sklearn_cfg['subset']

        self.show_image = self.config.get('show_image', False)
        self.max_frames = self.config.get('max_frames', -1)

        self.rotation_angle = self.config.get('rotation_angle', 0)

        self.margin_x = self.config.get('margin_x', 0)
        self.margin_y = self.config.get('margin_y', 0)

        keep_running = self.config.get('keep_running', False)
        self.set_keep_running(keep_running)

        q_maxsize = self.config.get('q_maxsize', -1)
        self.set_q_maxsize(q_maxsize)

        folder = self.config.get("folder", "")
        if not os.path.exists(folder):
            raise Exception(f"FolderSource: apply_config: Folder {folder} does not exist.")
        if not os.listdir(folder):
            raise Exception(f"FolderSource: apply_config: Folder {folder} is empty.")
        self.folder = folder

        bin_file = self.config.get("bin_file", "")

        originals_folder = self.config.get("originals_folder", "")
        pairs_source = self.config.get("pairs_source", "")

        if self.source == "pairs":
            self.img_generator = pairs_file_generator(originals_folder, pairs_source)
        elif self.source == "bin":
            bin_path = os.path.join(folder, bin_file)
            if not os.path.isfile(bin_path):
                raise Exception(f"FolderSource: apply_config: {bin_path} does not exists.")
            self.img_generator = bin_file_generator(bin_path)
            self.bin_file = bin_file
        elif self.source == "folder":
            self.img_generator = img_file_generator(folder)
        elif self.source == 'sklearn':
            self.img_generator = sklearn_file_generator(self.subset)
        else:
            raise Exception(f"FolderSource: apply_config: unknown source {self.source}.")

    def _generate_data(self):
        win_capt = "Source Image"
        try:
            data = next(self.img_generator)
            if data is None:
                print("FolderSource: Sending poison pill")
                return None

            if isinstance(data, FaceData) and self.rotation_angle != 0 and (self.cnt_frames % 2) == 1:
                img = data.get_face_image()
                h, w, _ = img.shape
                rotated_img = rotation(img, self.rotation_angle)
                data.set_face_image(rotated_img)

            if isinstance(data, FaceData) and (self.margin_x > 0 or self.margin_y > 0):
                img = data.get_face_image()
                h, w, _ = img.shape
                cropped_img = img[self.margin_y : h-self.margin_y, self.margin_x : w-self.margin_x]
                data.set_face_image(cropped_img)

            if self.show_image:
                img = data.get_source_image() if self.source in ['folder', 'pairs'] else data.get_face_image()
                cv2.imshow(win_capt, img)
                fname = f"c:/Datasets/tmp/{self.source}_{self.cnt_frames}.png"
                cv2.imwrite(fname, img)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("x") or key == ord("q"):
                    cv2.destroyWindow(win_capt)
                    self.stop()
                time.sleep(1)

            self.cnt_frames += 1
            if 0 < self.max_frames < self.cnt_frames:
                print(f"FolderSource: max_frames {self.max_frames} reached. Sending poison pill")
                return None

            return data
        except StopIteration:
            raise Empty

    def _release(self):
        print("FolderSource: exiting")

