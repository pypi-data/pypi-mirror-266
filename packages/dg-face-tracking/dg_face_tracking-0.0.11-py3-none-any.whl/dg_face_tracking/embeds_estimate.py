
import os
import numpy as np
from sklearn.metrics import pairwise_distances
from sklearn import metrics
import time

import pickle

import cv2
from deepface import DeepFace


def img_file_counter(folder_name: str) -> int:
    cnt = 0
    for fname in os.listdir(folder_name):
        if fname.endswith(".jpg"):
            cnt += 1

    return cnt

def load_images_from_folder(folder, model_name, min_count=2):
    images = []
    labels = []
    for label in os.listdir(folder):
        person_path = os.path.join(folder, label)
        if os.path.isdir(person_path):
            if img_file_counter(person_path) < min_count:
                continue
            for image_name in os.listdir(person_path):
                img_path = os.path.join(person_path, image_name)
                image_name_no_ext, ext = os.path.splitext(os.path.basename(image_name))
                if ext == ".emb":
                    continue

                emb_path = os.path.join(person_path, image_name_no_ext + "_" + model_name + ".emb")
                encoding = None
                if os.path.exists(emb_path):
                    with open(emb_path, 'rb') as f:
                        encoding = pickle.load(f)
                else:
                        print("----------Missing: " + emb_path)

                if encoding is not None:
                    print(img_path)
                    images.append(encoding)
                    labels.append(label)

    return images, labels


def evaluate_embeddings(embeddings, labels):
    # Compute pairwise distances between embeddings

    distances = pairwise_distances(embeddings, metric='cosine')
    np.fill_diagonal(distances, 0)

    # Convert labels to integers for silhouette score calculation
    label_dict = {label: idx for idx, label in enumerate(set(labels))}
    int_labels = np.array([label_dict[label] for label in labels])

    # Calculate silhouette score
    silhouette_score = metrics.silhouette_score(distances, int_labels, metric="precomputed")
    return silhouette_score


# Load face embedings and their labels
folder_path = "c:/Datasets/lfw"
model_name = "embeds_Facenet512"

t0 = time.time()
embeddings, labels = load_images_from_folder(folder_path, model_name, min_count=20)
t1 = time.time()
per_embedding = (t1 - t0) / len(embeddings)
print(f"Embeddings: Total {len(embeddings)}, {per_embedding}sec per embedding.")

# Evaluate embeddings
score = evaluate_embeddings(embeddings, labels)
print("Silhouette Score:", score)



