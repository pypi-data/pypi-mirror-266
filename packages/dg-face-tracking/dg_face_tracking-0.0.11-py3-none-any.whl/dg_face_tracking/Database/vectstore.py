import heapq
import os.path
from collections import deque
import time
import random
import pickle
from copy import deepcopy

import math
import numpy as np

import threading

from pathlib import Path
Path(__file__).resolve()


class VectStore:
    def __init__(self, max_size=16):
        self.max_size = max_size  # max number of vectors in a class
        self.vect_size = 0        # vectors dimensionality, set when first vector is added
        self.storage = dict()     # each key defines a class, vectors are stored in a deque
        self.labels = dict()      # {class_id: label}
        self.metadata = dict()    # class' metadata

    def is_present(self, class_id):
        return class_id in self.storage

    def class_size(self, class_id):
        if not self.is_present(class_id):
            return 0
        return len(self.storage[class_id])

    def max_class_size(self):
        max_size = 0
        for class_id in self.storage.keys():
            size = self.class_size(class_id)
            if size > max_size:
                max_size = size
        return max_size

    def max_metadata(self, key):
        max_data = None
        for val in self.metadata.values():
            try:
                data = val[key]
                if max_data is None:
                    max_data = data
                else:
                    if data is not None and max_data < data:
                        max_data = data
            except:
                continue
        return max_data

    @classmethod
    def load(cls, path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"VectStore: load: {path} does not exists")
        with open(path, 'rb') as f:
            db = pickle.load(f)
            return db

    def dump(self, path):
        db_copy = deepcopy(self)

        def run_dump(db, path):
            with open(path, 'wb') as f:
                pickle.dump(db, f)

        dump_thread = threading.Thread(target=run_dump, args=(db_copy, path))
        dump_thread.start()

    def size(self):
        _size = 0
        for vects in self.storage.values():
            _size += len(vects)
        return _size

    def list_entries(self):
        return [e for e in self.labels.values()]

    def del_entry(self, entry):
        for class_id, label in self.labels.items():
            if label == entry:
                self.delete(class_id)
                return True
        return False

    def add(self, class_id: str, vect: np.ndarray, label: str = "", **kvarg):
        if self.vect_size <= 0:
            self.vect_size = vect.size
        elif self.vect_size != vect.size:
            raise ValueError(f"VectStore: add: wrong vector size {vect.size}, should be {self.vect_size} ")

        if class_id not in self.storage:
            self.storage[class_id] = deque(maxlen=self.max_size)

        if class_id not in self.labels and label != "" and label != "unknown":
            self.labels[class_id] = label

        data = kvarg  # {k: v for k, v in kvarg.items()}

        # vect /= np.linalg.norm(vect)
        data['vect'] = vect

        self.storage[class_id].append(data)

    def add_metadata(self, class_id,  **kvarg):
        meta = kvarg # {k: v for k, v in kvarg.items()}
        self.metadata[class_id] = meta

    def delete(self, class_id):
        if class_id in self.storage:
            del self.storage[class_id]
        if class_id in self.labels:
            del self.labels[class_id]
        if class_id in self.metadata:
           del self.metadata[class_id]

    def update(self, class_id: str, label: str):
        self.labels[class_id] = label

    def __iter__(self):
        return self

    def __next__(self):
        if self.curr_class > self.end:
            raise StopIteration
        else:
            self.num += 1
            return self.num - 1

    def search(self, query: np.ndarray, max_results: int = 10, **kvarg):
        results = deque()
        if self.vect_size <= 0:
            return results

        if query.size != self.vect_size:
            raise ValueError(f"VectStore: search: size of query {query.size} differs from size of stored vectors {self.vect_size}")
        min_heap = []   # heap of (1-score, class_id) tuples

        for class_id in self.storage:
            if len(self.storage[class_id]) < 3:
                continue
            for data in self.storage[class_id]:
                vect = data['vect']
                score = vect @ query
                if len(min_heap) < max_results:
                    heapq.heappush(min_heap, (score, class_id))
                else:
                    if score > min_heap[0][0]:
                        heapq.heapreplace(min_heap, (score, class_id))

        while len(min_heap) > 0:
            res = heapq.heappop(min_heap)
            dist = 1 - res[0]
            class_id = res[1]
            label = self.labels[class_id] if class_id in self.labels else ""
            meta = self.metadata[class_id] if class_id in self.metadata else None

            results.appendleft((dist, class_id, label, meta))
        return results

    def analyze(self):
        for class_id, class_data in self.storage.items():
            if self.class_size(class_id) <= 1:
                continue
            dists = []
            n_data = len(class_data)
            for i in range(n_data-1):
                data_i = class_data[i]
                embeds_i = data_i['vect']
                for j in range(i+1, n_data):
                    data_j = class_data[j]
                    embeds_j = data_j['vect']
                    dists.append(1 - embeds_i @ embeds_j)

            mean_dist = sum(dists) / len(dists)
            deviations = [(x - mean_dist) ** 2 for x in dists]
            variance = math.sqrt(sum(deviations) / len(dists))
            if class_id in self.metadata:
                self.metadata[class_id]['mean_dist'] = mean_dist
                self.metadata[class_id]['variance'] = variance
            else:
                self.metadata[class_id] = {'mean_dist':mean_dist, 'variance':variance}

    def get_data(self):
        X = []
        y = []
        for class_id, class_data in self.storage.items():
            for data in class_data:
                X.append(data['vect'])
                y.append(class_id)
        return np.asarray(X), np.asarray(y)

    def strip_small_classes(self, min_in_class):
        list2del = []
        for class_id in self.storage:
            if self.class_size(class_id) < min_in_class:
                list2del.append(class_id)

        for class_id in list2del:
            self.delete(class_id)

    def extract_random(self, min_class=-1):
        valid_class_ids = [id for id in self.storage.keys() if self.class_size(id) > min_class]
        if len(valid_class_ids) == 0:
            return None, None, None
        class_id = random.choice(valid_class_ids)
        label = self.labels[class_id]
        item_id = random.randrange(self.class_size(class_id))
        data = self.storage[class_id][item_id]
        vect = data['vect']
        del self.storage[class_id][item_id]

        return class_id, vect, label

    def bootstrap(self, min_class=2, th=-1.0):
        n_total = 0
        n_good = 0
        for class_id, class_data in self.storage.items():
            n_data = len(class_data)
            if n_data < min_class:
                continue
            for _ in range(n_data):
                data = class_data.popleft()
                embeds = data['vect']
                results = self.search(embeds, min_class)
                n_total += 1
                if len(results) > 0:
                    dist, nearest_class_id, label = self.proc_results(results)
                    if class_id == nearest_class_id:
                        if th > 0 and dist > th:
                            continue
                        n_good += 1
                    else:
                        print("Error!")
                class_data.append(data)
        accuracy = n_good / n_total if n_total > 0 else None
        return accuracy

    def proc_results(self, results):
        classes = {}
        for res in results:
            dist, class_id, label = res
            key = (class_id, label)
            if key not in classes:
                classes[key] = 1 - dist
            else:
                classes[key] += 1 - dist

        best_score = 0
        best_key = None
        for key, score in classes.items():
            if score > best_score:
                best_key = key
                best_score = score

        for res in results:
            dist, class_id, label = res
            if class_id == best_key[0]:
                return dist, class_id, label



if __name__ == "__main__":
    vect_size = 2500
    vects = [
    np.zeros(vect_size, dtype=float),
    np.zeros(vect_size, dtype=float),
    np.zeros(vect_size, dtype=float)
    ]

    vects[0][0] = 1.0
    vects[1][1] = 1.0
    vects[2][2] = 1.0

    max_size = 100
    vstore = VectStore(max_size=max_size)

    start = time.time()
    for class_id, v in enumerate(vects):
        for i in range(max_size + 10):
            d = np.random.rand(vect_size) * 0.1
            d = v + d
            d = d / np.linalg.norm(d)
            vstore.add(str(class_id), d)
    elapsed = 1000 * (time.time() - start)

    print(f"Insert time: {elapsed / vstore.size()}ms")

    q0 = np.zeros(vect_size, dtype=float)
    q0[1] = 1.0

    n_queries = 100
    queries = []
    for _ in range(n_queries):
        q = q0 + np.random.rand(vect_size) * 0.1
        q = q / np.linalg.norm(q)
        queries.append(q)

    start = time.time()
    for q in queries:
        results = vstore.search(q, max_results=10)
        pass
    elapsed = 1000 * (time.time() - start)
    print(f"Query time: {elapsed/n_queries}ms")
    pass




