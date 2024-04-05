import os
import sys
import threading
import time
from queue import Queue
from typing import Any, List

from pathlib import Path
Path(__file__).resolve()

from ..config_rt import ConfigRT
from ..Process.dg_process import DG_Process
from ..Data.basedata import PoisonPill


class Processor(threading.Thread):
    """
    Base abstract class for various processors (one input queue, several output queues)
    Methods to implement in subclasses:
    apply_config : apply real-time config
    process : process data coming in input queue, and sent to several output queues
    """
    def __init__(self, proc_id: str, q_in: Queue, runs_event, config_name):
        super().__init__()
        self.proc_id = proc_id
        self.q_in = q_in
        self.q_out_map: dict = {}

        self.stop_event = threading.Event()
        self.runs_event = runs_event if runs_event is not None else threading.Event()

        # Starting real-time config tracking service
        self.config = ConfigRT(config_name)
        try:
            self.apply_config()
        except Exception as e:
            self.config.stop()
            raise e

    def add_q_out(self, destination, q_out):
        self.q_out_map[destination] = q_out

    def _in_data(self) -> Any:
        """
        Get data from queue
        :return: data item,if there is something in the queue, otherwise None
        """
        try:
            d = self.q_in.get_nowait()
            if d is None:
                d = PoisonPill()
            return d
        except:
            return None

    def _out_data(self, processed_data: List) -> None:
        """
        Send data to several output queues
        :param processed_data: list of data to send
        :return:
        """
        for data in processed_data:
            if data is not None:
                if isinstance(data, PoisonPill):
                    # send poison pill to all output q's
                    for q_out in self.q_out_map.values():
                        time.sleep(5)   # TODO: change it!!!!!
                        q_out.put_nowait(None)
                else:
                    destinations = data.pop_property('destinations')
                    if destinations is None:
                        print("Processor: _out_data: No destinations set in data")

                    for dest in destinations:
                        q_out = self.q_out_map.setdefault(dest, None)
                        if q_out is not None:
                            q_out.put_nowait(data)
                        else:
                            print(f"Processor: _out_data: Failed to send data to destination: {dest}")
            else:
                print(f"Processor: _out_data: None in processed data")

    def apply_config(self) -> None:
        raise Exception("Processor process() method must be implemented in subclass.")

    def process(self, data) -> List:
        raise Exception("Processor process() method must be implemented in subclass.")

    def stop(self):
        self.config.stop()
        self.stop_event.set()

    def is_stopped(self) -> bool:
        return self.stop_event.is_set()

    def wait2run(self):
        self.runs_event.wait()

    def warm_up(self):
        """
        Set the run_event to signal that the service is ready to accept data
        Override in subclasses if some warm-up actions are needed
        """
        self.runs_event.set()

    def _release(self) -> None:
        """
        Release acquired resources and empty input queue
        :return:
        """
        while not self.q_in.empty():
            try:
                self.q_in.get_nowait()
            except:
                break

    def run(self) -> None:
        """
        Override run() of Thread class
        """
        self.warm_up()

        while not self.stop_event.is_set():
            data = self._in_data()
            if data is not None:
                if isinstance(data, PoisonPill):
                    print(f"Processor {self.proc_id}: got poison pill")
                    self._out_data([data])
                else:
                    try:
                        processed_data = self.process(data)
                        self._out_data(processed_data)
                        time.sleep(0.01)
                    except Exception as e:
                        print(f"Processor {self.proc_id}: " + str(e))
                        continue
            else:
                time.sleep(0.01)
        self._release()


def run_processor(params={}):
    print("Running run_processor")

    if 'Processor' not in params or 'config' not in params:
        print("run_embedder: missing data in params")
        return

    try:
        Processor = params['Processor']
        proc_id = params['proc_id']
        q_in = params['q_in']
        q_out_map = params['q_out_map']
        config = params['config']
        runs_event = params['runs_event']
        proc = Processor(proc_id, q_in, runs_event, config_name=config)
        for dest, q in q_out_map.items():
            proc.add_q_out(dest, q)
    except Exception as e:
        print("run_embedder: missing data in params")
        return

    proc.start()
