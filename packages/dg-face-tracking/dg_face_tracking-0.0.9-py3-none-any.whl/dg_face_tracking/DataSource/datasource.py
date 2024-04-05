import os
import sys

import time
import threading, multiprocessing
from queue import Queue, Empty, Full

from typing import Union, Any

from pathlib import Path
Path(__file__).resolve()

from ..config_rt import ConfigRT


class DataSource(threading.Thread):
    """
    Base abstract class for various datasources
    Methods to implement in subclasses:
    _generate_data : returns some data
    _release: release resources, like cameras or streams
    """
    def __init__(self, source_id: str,
                 runs_event: Union[threading.Event, multiprocessing.Event], config_name: str):
        """
        DataSource Constructor
        :param q_out: Queue: Output data stream
        """
        self.source_id = source_id
        self.keep_running = False

        self.q_out_list = []
        self.q_timeout = 1   # 1sec default q timeout
        self.q_maxsize = -1  # max size of output q, unlimited by default (pause if q reaches that size)

        self.stop_event = threading.Event()
        self.runs_event = runs_event if runs_event is not None else threading.Event()

        # Starting real-time config tracking service
        config_name = config_name if config_name != "" else source_id
        self.config = ConfigRT(config_name)
        try:
            self.apply_config()
        except Exception as e:
            self.config.stop()
            raise e

        super(DataSource, self).__init__()

    def add_q_out(self, q_out: Union[Queue, multiprocessing.Queue]):
        if q_out is not None:
            self.q_out_list.append(q_out)

    def set_q_maxsize(self, maxsize: int):
        self.q_maxsize = maxsize

    def set_keep_running(self, keep_running: bool):
        self.keep_running = keep_running

    def stop(self):
        """
        Stop DataSource service
        """
        self.stop_event.set()


    def is_stopped(self) -> bool:
        """
        Check if the service is to be stopped
        :return: bool
        """
        return self.stop_event.is_set()

    def is_running(self) -> bool:
        """
        Check if the service is running
        :return: bool
        """
        return self.runs_event.is_set()

    def get_id(self):
        """
        Returns source id
        :return: str
        """
        return self.source_id

    def wait2run(self, time2wait: Union[None, float] = None) -> bool:
        """
        Wait for the event to be set, returns True
        If time2wait is None:  wait indefinitely
        If time2wait is a float: wait specified time, if event is not set after this time, then return False
        """
        return self.runs_event.wait(time2wait)

    def put2q(self, item: Any):
        for q_out in self.q_out_list:
            while 0 < self.q_maxsize < q_out.qsize():
                q_out.get_nowait()
                time.sleep(0.01)
            while True:
                try:
                    q_out.put_nowait(item)
                    break
                except Full:
                    # Discard the oldest
                    q_out.get_nowait()
                    print(f"DataSource {self.source_id}: run : queue is full.")


    def run(self):
        """
        Override run() of Thread class
        """
        self.runs_event.set()
        while not self.is_stopped():
            try:
                # apply config changes, if any
                if self.config.is_modified():
                    self.apply_config()
                # generate data (one item or a list of items)
                items = self._generate_data()
                if items is not None:
                    if not isinstance(items, list):
                        items = [items]
                    for item in items:
                        self.put2q(item)
            except Empty as e:
                # generator signals the end of data stream
                if not self.keep_running:
                    print("DataSource: run: sending poison pill")
                    self.put2q(None)  # poison pill
                    break
            except Exception as e:
                print("Datasource: run: " + str(e))
            time.sleep(0.001)
        # release all resources on exit
        self._release()
        self.config.stop()
        self.config.join()
        self.runs_event.clear()
        self.stop_event.set()
        print("DataSource: run: exiting")

    def apply_config(self) -> None:
        """
        Abstract method, to be implemented in derived classes.
        Read from config.
        :return: None
        """
        raise Exception("Processor process() method must be implemented in subclass.")

    def _generate_data(self):
        """
        Abstract method, to be implemented in derived classes.
        Generate some data.
        :return: Any: Data to be pushed to output stream
        """
        raise Exception("DataSource _generate_data() method must be implemented in subclass.")

    def _release(self):
        """
        Abstract method, to be implemented in derived classes.
        Release any acquired resources.
        """
        raise Exception("DataSource _release() method must be implemented in subclass.")




            

