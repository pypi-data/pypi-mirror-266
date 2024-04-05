import pickle
import numpy as np
import cv2

from Consumers.pairwise_stats import FacePair

def main():
    fname_bin = "c:/Dev/Data/ml-data/glint360k/bin_pairs.pkl"
    with open(fname_bin, "rb") as f:
        pairs_bin = pickle.load(f)

    fname_skl = "c:/Dev/Data/ml-data/glint360k/skl_pairs.pkl"
    with open(fname_skl, "rb") as f:
        pairs_skl = pickle.load(f)

    print(f"Bin len: {len(pairs_bin)};  Skl len: {len(pairs_skl)}")

    th = 1.53
    n_err_bin = n_err_skl = 0
    err_list = []
    for idx in pairs_bin.keys():
        pair_bin: FacePair = pairs_bin[idx]
        pair_bin.verify(th)

        pair_skl: FacePair = pairs_skl[idx]
        pair_skl.verify(th)

        if pair_bin.actual != pair_bin.target:
            n_err_bin += 1
        if pair_skl.actual != pair_skl.target:
            n_err_skl += 1

        dist_diff = abs(pair_bin.dist - pair_skl.dist)

        if pair_bin.actual == pair_bin.target and pair_bin.actual != pair_skl.actual:
            for i in range(1,3):
                img_bin = pair_bin.img1 if i == 1 else pair_bin.img2
                img_skl = pair_skl.img1 if i == 1 else pair_skl.img2
                fname_img_bin = f"C:/Dev/dg_face_tracking/embeds_eval/images/bin_{idx}_{i}.png"
                fname_img_skl = f"C:/Dev/dg_face_tracking/embeds_eval/images/skl_{idx}_{i}.png"
                cv2.imwrite(fname_img_bin, img_bin)
                cv2.imwrite(fname_img_skl, img_skl)
            err_list.append((dist_diff, idx))
            # print(f"idx: {idx}  target: {pair_bin.target}; dist_bin: {pair_bin.dist};  dist_skl: {pair_skl.dist}")

    err_list.sort(reverse=True)

    fname_err = "c:/Dev/Data/ml-data/glint360k/err_list.pkl"
    with open(fname_err, "wb") as f:
        pickle.dump(err_list, f)

    print(f"Err number: bin: {n_err_bin};  skl: {n_err_skl}")

if __name__ == "__main__":
    main()


