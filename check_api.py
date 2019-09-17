import os
import glob
import mra_slices
import requests
import vessel_segmentation
import numpy as np
import json
import cv2

def run(study_dir):
    for subject_dir in sorted(glob.glob(os.path.join(study_dir, "*")), reverse=True):
        print subject_dir
        dicom_fpath_list = glob.glob(os.path.join(subject_dir, "*"))
        print "BUILD MRA VOLUME"
        slices = mra_slices.MRASlices(dicom_fpath_list)
        print "EXTRACT VOLUME"
        vessel = vessel_segmentation.extract(slices.volume)
        """
        for z in range(vessel.shape[2]):
            cv2.imwrite("/Users/nishimori-m/Downloads/temp/%03d.png" % z, vessel[:,:,z])
        break
        """
        print "CALL API"
        xs, ys, zs = np.where(vessel > 0)
        n = len(xs)
        i = np.random.randint(n)
        j = np.random.randint(n)
        r = requests.get("http://127.0.0.1:8888/v1/vessel_length/calculate", params={
                "subject_dir": subject_dir,
                "src_sop_instance_uid": slices.mra_slices[zs[i]].SOPInstanceUID,
                "sx": xs[i],
                "sy": ys[i],
                "dst_sop_instance_uid": slices.mra_slices[zs[j]].SOPInstanceUID,
                "tx": xs[j],
                "ty": ys[j]
            })
        print r.text
        res = json.loads(r.text)
        length = res["length"]
        path = res["path"]
        img = np.max(slices.volume, axis=2)
        img = img.astype(np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        for p in path:
            img[p["x"], p["y"], 0] = 255
        cv2.imwrite("/tmp/%s.png" % subject_dir.replace("/", "_"), img)
        cv2.imwrite("/tmp/%s_vessel.png" % subject_dir.replace("/", "_"), np.max(vessel, axis=2))
        for z in range(slices.volume.shape[2]):
            img = slices.volume[:,:,z]
            img = (128.0 / np.max(img)) * img
            img = img.astype(np.uint8)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            for p in path:
                if p["z"] == z:
                    img[p["x"]-1:p["x"]+2, p["y"]-1:p["y"]+2, 0] = 255
            cv2.imwrite("/tmp/%s_%03d_%s.png" % (subject_dir.replace("/", "_"), z, slices.mra_slices[z].SOPInstanceUID), img[:,:,::-1])

if __name__ == "__main__":
    """
    python check_api.py --study_dir "/home/nishimori/.eir/aneurysm/dicom"
    """
    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--study_dir', type=str, required=True)
    args = parser.parse_args()
    run(args.study_dir)
