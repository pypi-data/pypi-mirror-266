import sys

from multiprocessing import Process, Queue, Event


class DG_Process:
    def __init__(self, proc_id, target=None, params={}):
        self.proc = None
        self.proc_id = proc_id
        self.target = target
        self.params = params
        self.q_in = params.setdefault('q_in', Queue())
        self.q_out_map = {}
        self.runs_event = Event()

    def add_q_out(self, proc_id: str, q: Queue):
        self.q_out_map[proc_id] = q

    def start(self):
        if self.target is not None and isinstance(self.params, dict):
            print(f"Starting {self.proc_id} process...")
            self.params['q_in'] = self.q_in
            self.params['q_out_map'] = self.q_out_map
            self.params['runs_event'] = self.runs_event
            self.proc = Process(target=self.target, kwargs={'params': self.params})
            self.proc.start()
        else:
            if self.target is None:
                raise ValueError("DG_Process: start: target is not set.")
            elif isinstance(self.params, dict):
                raise ValueError("DG_Process: start: params should be passed as dict.")
            else:
                raise Exception("DG_Process: start: failed.")

    def is_alive(self):
        return self.runs_event.is_set()

    def wait2run(self):
        self.runs_event.wait()
        print(f"{self.proc_id} process running!")

    def stop(self):
        if self.proc is not None and self.is_alive():
            self.proc.kill()

    def join(self):
        self.proc.join()

