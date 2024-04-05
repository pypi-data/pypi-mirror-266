import pickle
from sklearn.preprocessing import normalize
from sklearn.datasets import fetch_lfw_pairs
import cv2
import numpy as np
import time
from tqdm import tqdm


def load_binary_dataset(dataset_path, embeds_path, image_size):
    """
    Load and preprocess a binary dataset.

    Args:
    - path (str): Path to the binary dataset.
    - image_size (tuple): Size to which the images will be resized.
    - last_index (int, optional): Last index to be considered in the dataset.

    Returns:
    - list: Preprocessed data list.
    - list: Corresponding 'issame' list.
    """
    # Loading the binary dataset

    with open(dataset_path, 'rb') as file:
        _, issame_list = pickle.load(file, encoding='bytes')  # Python 3 compatibility

    with open(embeds_path, 'rb') as file:
        embeddings_list = pickle.load(file, encoding='bytes')  # Python 3 compatibility

    embeddings_all = np.array(embeddings_list)

    return embeddings_all, issame_list


def calculate_accuracy(threshold, dist, actual_issame):
    """
    Calculate the accuracy of the model.

    Args:
    - threshold (float): Threshold for determining whether faces match.
    - dist (np.array): Array of distances between face pairs.
    - actual_issame (list): Ground truth for whether faces are the same.

    Returns:
    - float: True positive rate.
    - float: False positive rate.
    - float: Overall accuracy.
    """
    predict_issame = np.less(dist, threshold)
    tp = np.sum(np.logical_and(predict_issame, actual_issame))
    fp = np.sum(np.logical_and(predict_issame, np.logical_not(actual_issame)))
    tn = np.sum(np.logical_and(np.logical_not(predict_issame), np.logical_not(actual_issame)))
    fn = np.sum(np.logical_and(np.logical_not(predict_issame), actual_issame))

    tpr = float(tp) / (tp + fn) if (tp + fn) else 0
    fpr = float(fp) / (fp + tn) if (fp + tn) else 0
    acc = float(tp + tn) / dist.size

    return tpr, fpr, acc

def compute_distance(embeddings_all):
    """
    Compute the distances between pairs of embeddings.

    Args:
    - embeddings_all (np.array): Array of normalized embeddings.

    Returns:
    - np.array: Distances between each pair of embeddings.
    """
    embeddings1 = embeddings_all[0::2]
    embeddings2 = embeddings_all[1::2]
    diff = np.subtract(embeddings1, embeddings2)
    dist = np.sum(np.square(diff), axis=1)
    return dist


def main():
    # Defining dataset path and preprocessing parameters
    # options 'lfw', 'cfp_fp', "agedb_30": all bin files are available in Mercury in the same path
    dataset = 'lfw'
    embeds = 'mobileface512_noflip'
    dataset_path = f'C:/Dev/data/ml-data/glint360k/{dataset}.bin'
    embeds_path = f'C:/Dev/data/ml-data/glint360k/embeds_{embeds}.bin'
    image_size = (112, 112)

    lfw_pairs = fetch_lfw_pairs(subset='10_folds', color=True, resize=1)

    # Loading and preprocessing the dataset
    embeddings, issame_list = load_binary_dataset(dataset_path, embeds_path, image_size)
    # Calculating accuracy
    dist = compute_distance(embeddings)

    threshold = 0.1
    while threshold <= 2.5:
        tpr, fpr, acc = calculate_accuracy(threshold, dist, issame_list)
        print(f"Threshold: {threshold:.3f}, True Positive Rate: {tpr:.3f},  False Positive Rate: {fpr:.3f}, Accuracy: {acc:.3f}")
        threshold += 0.01


if __name__ == "__main__":
    main()