import sys
import os
import pickle

import numpy as np

sys.path.append(os.getcwd())

from dg_face_tracking.Consumers.consumer import Consumer
from dg_face_tracking.Database.LocalDBAdapter import LocalDBAdapter
from dg_face_tracking.Data.basedata import BaseData
from dg_face_tracking.Data.frame_data import FrameData
from dg_face_tracking.Data.face_data import EmbeddedFaceData

from dg_face_tracking.Database.vectstore import VectStore

from dg_face_tracking.config_rt import ConfigRT

default_catalogue_path = "C:/Dev/Datasets/SQLite"
default_datasets_path = "C:/Dev/Datasets"

default_config = {
}


class EmbedsWriter(Consumer):
    """
    EmbedWriter: write pickled embeds
    """
    def __init__(self, proc_id, q_in, config_name):
        """
        LocalDBWriter constructor
        """
        print("EmbedsWriter init")

        self.embeds_type = "embeds"

        self.embeds_all = []
        self.write_bin = False
        self.write_embeds = False
        self.write_vect_db = False
        self.bin_path = ""
        self.vect_db_path = ""

        self.vect_db = VectStore(512)

        if config_name is None:
            config_name = self.__class__.__name__
        self.config = ConfigRT(config_name)
        try:
            self.apply_config()
        except Exception as e:
            self.config.stop()
            raise e

        super(EmbedsWriter, self).__init__(proc_id, q_in)

    def stop(self):
        """
        Stop adapter
        """
        self.config.stop()
        self.config.join()
        super(EmbedsWriter, self).stop()
        print("EmbedsWriter stopped")

    def apply_config(self):
        """
        Try to apply config.
        If failed, but there is a valid configuration setup already, the new one will be ignored
        """
        if not self.config.is_modified():
            return

        self.embeds_type = self.config.get("embeds_type", "mobilenet_512")

        self.write_bin = self.config.get("write_bin", False)
        self.write_embeds = self.config.get("write_embeds", False)
        self.write_vect_db = self.config.get("write_vect_db", False)

        self.bin_path = self.config.get("bin_path", "")
        self.vect_db_path = self.config.get("vect_db_path", "")

        write_embeds: False
        write_vect_db: True

    def consume(self, data: BaseData) -> None:
        """
        data dispatcher
        :param data:  one of BaseData subclasses
        """
        if data.get_data_type() == "embedded_face_data":
            source_file = data.get_property('source_file')
            embeds = data.get_property('embeddings')
            face_id = data.get_property('face_id')
            label = data.get_property('label')

            self.vect_db.add(face_id, np.array(embeds), label)

            if self.write_bin:
                self.embeds_all.append((int(face_id), embeds))
                n_embeds = len(self.embeds_all)
                if n_embeds % 100 == 0:
                    print(f"EmbedsWriter: collected {n_embeds}")
            if self.write_embeds:
                if source_file is not None:
                    fname, _ = os.path.splitext(source_file)
                    fname += "_" + self.embeds_type + ".emb"
                    with open(fname, 'wb') as f:
                        print("EmbedsWriter: writing ", fname)
                        pickle.dump(embeds, f)
            return

    def _release(self):
        acc = self.vect_db.bootstrap(min_class=20)
        print(f"Bootstrap accuracy: {acc:.3f}")

        if self.write_bin:
            self.embeds_all = sorted(self.embeds_all)
            face_id_list = [embeds[0] for embeds in self.embeds_all]
            for i in range(1, len(self.embeds_all)):
                if self.embeds_all[i-1][0] + 1 != self.embeds_all[i][0]:
                    print("!!!!!!! EmbedsWriter: wrong order in embeddings list")
            self.embeds_all = [embeds[1] for embeds in self.embeds_all]
            fname = os.path.join(self.bin_path, f"embeds_{self.embeds_type}.bin")
            with open(fname, 'wb') as f:
                print("EmbedsWriter: writing all embeds in bin: ", fname)
                pickle.dump(self.embeds_all, f)

        if self.write_vect_db:
            fname = os.path.join(self.vect_db_path, self.embeds_type+".pkl")
            with open(fname, 'wb') as f:
                print("EmbedsWriter: writing vect_db in: ", fname)
                pickle.dump(self.vect_db, f)

        self.config.stop()
        self.config.join()















