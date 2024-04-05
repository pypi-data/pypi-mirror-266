import time
import threading
from queue import Empty

class Consumer(threading.Thread):
    def __init__(self, proc_id, q_in):
        super(Consumer, self).__init__()
        self.proc_id = proc_id
        self.q_in = q_in

        self.stop_event = threading.Event()
        self.runs_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def is_stopped(self):
        return self.stop_event.is_set()

    def wait2run(self):
        self.runs_event.wait()

    def warm_up(self):
        """
        Set the run_event to signal that the service is ready to accept data
        Override in subclasses if some warm-up actions are needed
        """
        self.runs_event.set()

    def consume(self, data):
        raise Exception("Consumer consume() method must be implemented in a subclass.")

    def _release(self):
        while not self.q_in.empty():
            try:
                self.q_in.get_nowait()
            except:
                break

    def run(self):
        """
        Override run() of Thread class
        """
        self.warm_up()
        while not self.stop_event.is_set():
            try:
                data = self.q_in.get_nowait()
                if data is None:
                    print("Consumer: got poison pill")
                    break
                self.consume(data)
            except Empty:
                time.sleep(0.01)
                continue
            except Exception as e:
                print(f"Consumer {self.proc_id}: run: " + str(e))
                continue

        self._release()
