import time
import threading
from queue import Queue, Empty


class DBAdapterEmptyException(Empty):
    """
    To be thrown when there is no more data to read
    """
    pass


class DBAdapter(threading.Thread):
    """
    Base class for Dataset adapters
    """
    def __init__(self):
        self.q = Queue()
        self.stop_event = threading.Event()

        super(DBAdapter, self).__init__()

    def stop(self):
        self.q.join()
        self.stop_event.set()
        self.join()

    def is_stopped(self):
        return self.stop_event.is_set()

    def disconnect(self):
        raise Exception("DBAdapter: disconnect() method must be implemented in subclass.")

    def connect2db(self):
        raise Exception("DBAdapter: connect2db() method must be implemented in subclass.")

    def _run_query(self, data):
        raise Exception("DBAdapter: query() method must be implemented in subclass.")

    def run(self):
        """
        Overrides run() of Thread class
        """
        self.connect2db()

        while not self.stop_event.is_set():
            try:
                query = self.q.get_nowait()
                try:
                    self._run_query(query)
                    self.q.task_done()
                except Exception as e:
                    print("DBAdapter: run: " + str(e))
                time.sleep(0.1)
            except Exception as e:
                # no data in q
                time.sleep(0.1)
                continue

        self.disconnect()
