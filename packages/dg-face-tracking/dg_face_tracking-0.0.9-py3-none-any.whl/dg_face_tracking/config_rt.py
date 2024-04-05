import os
import time
import threading

import config

class ConfigRT(threading.Thread):
    def __init__(self, name: str, autostart=True):
        super(ConfigRT, self).__init__()

        self.name = name
        self.modified_time = 0.0

        self.path = f"Configs/{name}"
        if ".cfg" not in name:
            self.path += ".cfg"

        self.stop_event = threading.Event()
        self.lock = threading.Lock()

        self.modified = True

        try:
            self._config = self._load_config()
            if autostart:
                self.start()
        except Exception as e:
            print("ConfigRT: unable to start config service: " + str(e))

    def is_modified(self):
        return self.modified

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, cfg):
        self.lock.acquire()
        self._config = cfg
        self.lock.release()

    def get(self, attr, default=None):
        """
        Tries to get attr from config.
        If no such key, return default. If no default provided, raise the exception.
        """
        self.lock.acquire()
        try:
            res = self.config[attr]
        except:
            if default is not None:
                res = default
            else:
                self.lock.release()
                raise KeyError(f"ConfigRT: get: missing key {attr}, no default provided")
        self.lock.release()
        self.modified = False

        return res

    def stop(self):
        if self.is_alive():
            self.stop_event.set()
            self.join()

    def _load_config(self):
        if os.path.exists(self.path) and os.path.isfile(self.path):
            modified_time = os.path.getmtime(self.path)
            if modified_time > self.modified_time or self.config is None:
                cfg = config.Config(self.path)
                self.modified_time = modified_time
                self.modified = True
                return cfg
            else:
                return None
        else:
            self.config = None
            raise Exception(f"No config file for {self.name}")


    def run(self):
        """
        Override run() of Thread class
        """
        while not self.stop_event.is_set():
            try:
                config = self._load_config()
                if config != None:
                    self.config = config
            except Exception as e:
                print("Config: run: " + str(e))
            time.sleep(5)

