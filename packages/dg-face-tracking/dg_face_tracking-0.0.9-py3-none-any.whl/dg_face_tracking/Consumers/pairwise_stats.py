import sys
import os
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import cv2
import time

import pickle

sys.path.append(os.getcwd())

from dg_face_tracking.Consumers.consumer import Consumer
from dg_face_tracking.Data.basedata import BaseData

from dg_face_tracking.config_rt import ConfigRT

default_catalogue_path = "C:/Dev/Datasets/SQLite"
default_datasets_path = "C:/Dev/Datasets"

default_config = {
}


class FacePair:
    threshold = 1.5
    metric = 'l2'

    def __init__(self, target):
        self.emb1 = None
        self.emb2 = None
        self.img1 = None
        self.img2 = None
        self.dist = None
        self.actual = -1
        self.target = target == 1

    def add_embedding(self, embedding, img=None):
        if self.emb1 is None:
            self.emb1 = embedding
            self.img1 = img
        elif self.emb2 is None:
            self.emb2 = embedding
            self.img2 = img
            self.compute_dist()
        else:
            raise Exception("FacePair: add_embedding: trying to add embedding to a full pair.")

    def compute_dist(self):
        if self.emb1 is not None and self.emb2 is not None:
            if FacePair.metric == "l2":
                diff = np.subtract(self.emb1, self.emb2)
                self.dist = np.sum(np.square(diff))

    def verify(self, threshold):
        if self.emb1 is None or self.emb2 is None:
            return False
        if self.dist is None:
            self.compute_dist()
        self.actual = (self.dist < threshold) if self.dist is not None else None
        return True


class PairwiseStats(Consumer):
    """
    EmbedWriter: write pickled embeds
    """
    def __init__(self, proc_id, q_in, config_name):
        """
        LocalDBWriter constructor
        """
        print("PairwiseStats init")

        self.embeds_type = "embeds"
        self.show_errors = False

        self.face_pairs = {}

        if config_name is None:
            config_name = self.__class__.__name__
        self.config = ConfigRT(config_name)
        try:
            self.apply_config()
        except Exception as e:
            self.config.stop()
            raise e

        super(PairwiseStats, self).__init__(proc_id, q_in)

    def stop(self):
        """
        Stop adapter
        """
        self.config.stop()
        self.config.join()
        super(PairwiseStats, self).stop()
        print("PairwiseStats stopped")

    def apply_config(self):
        """
        Try to apply config.
        If failed, but there is a valid configuration setup already, the new one will be ignored
        """
        if not self.config.is_modified():
            return

        self.show_errors = self.config.get("show_errors", False)

        threshold = self.config.get("threshold", -1)
        if threshold > 0:
            FacePair.threshold = threshold

        metric = self.config.get("metric", "l2")
        if metric in ["l2", "cosine"]:
            FacePair.metric = metric

    def consume(self, data: BaseData) -> None:
        """
        data dispatcher
        :param data:  one of BaseData subclasses
        """
        if data.get_data_type() == "embedded_face_data":
            embeds = data.get_property('embeddings')
            face_id = data.get_property('pair_idx')
            face_img = data.get_property('face_image')
            target = data.get_property('target')
            if embeds is None or face_id is None or target is None:
                print("PairwiseStats: consume: insufficient data.")
            else:
                face_pair = self.face_pairs.setdefault(face_id, FacePair(target))
                face_pair.add_embedding(embeds, face_img)
            return

    def compute_stats(self):
        best_th = 0.0
        best_acc = 0.0

        th = 0.01
        while th <= 2.0:
            targets = []
            actuals = []
            for pair in self.face_pairs.values():
                if pair.verify(th):
                    if pair.actual is not None:
                        actuals.append(pair.actual)
                        targets.append(pair.target)
            accuracy = accuracy_score(targets, actuals)
            precision = precision_score(targets, actuals)
            recall = recall_score(targets, actuals)
            print(f"Threshold: {th:.3f}, Accuracy: {accuracy:.3f},  Precision: {precision:.3f}, Recall: {recall:.3f}")
            if accuracy > best_acc:
                best_acc = accuracy
                best_th = th
            th += 0.01

        errors = []
        for pair in self.face_pairs.values():
            if pair.verify(best_th):
                if pair.actual is not None and pair.actual != pair.target:
                    errors.append(pair)
                    if self.show_errors:
                        img1 = pair.img1
                        img2 = pair.img2
                        h1, w1 = img1.shape[:2]
                        h2, w2 = img2.shape[:2]

                        if h2 > h1:
                            img1 = cv2.copyMakeBorder(img1, top=0, bottom=(h2-h1), left=0, right=0, borderType=cv2.BORDER_CONSTANT)
                        elif h1 > h2:
                            img2 = cv2.copyMakeBorder(img2,  top=0, bottom=(h1-h2), left=0, right=0, borderType=cv2.BORDER_CONSTANT)
                        if w2 > w1:
                            img1 = cv2.copyMakeBorder(img1, top=0, bottom=0, left=0, right=(w2-w1), borderType=cv2.BORDER_CONSTANT)
                        elif w1 > w2:
                            img1 = cv2.copyMakeBorder(img1,  top=0, bottom=0, left=0, right=(w1-w2), borderType=cv2.BORDER_CONSTANT)
                        img = np.concatenate((img1, img2), axis=1)
                        cv2.imshow("pair", img)
                        cv2.waitKey(1)
                        time.sleep(1)

        fname = "c:/Dev/dg_face_tracking/embeds_eval/errors/err_pairs.pkl"
        with open(fname, "wb") as f:
            pickle.dump(errors, f)

    def _release(self):
        self.compute_stats()
        self.config.stop()
        self.config.join()















