import json
from flask import Flask, request
import os, glob
import mra_slices, vessel_segmentation

app = Flask(__name__)

@app.route("/v1/vessel_length/calculate")
def _calculate_vessel_length():
    subject_dir = request.args.get("subject_dir")
    src_sop_instance_uid = request.args.get("src_sop_instance_uid", type=str)
    sx0 = request.args.get("sx", type=int)
    sy0 = request.args.get("sy", type=int)
    dst_sop_instance_uid = request.args.get("dst_sop_instance_uid", type=str)
    tx0 = request.args.get("tx", type=int)
    ty0 = request.args.get("ty", type=int)
    slices = mra_slices.MRASlices(glob.glob(os.path.join(subject_dir, "*.dcm")))
    sz0, tz0 = -1, -1
    for z in range(slices.volume.shape[2]):
        if slices.mra_slices[z].SOPInstanceUID == src_sop_instance_uid:
            sz0 = z
        if slices.mra_slices[z].SOPInstanceUID == dst_sop_instance_uid:
            tz0 = z
    W, H, D = slices.volume.shape
    path = []
    if ((0 <= sx0 < W) and (0 <= sy0 < H) and (0 <= sz0 < D) and (0 <= tx0 < W) and (0 <= ty0 < H) and (0 <= tz0 < D)):
        sx, sy, sz = sx0, sy0, sz0
        tx, ty, tz = tx0, ty0, tz0
        factor = 2.7
        for i in range(3):
            print "FACTOR = %.3f" % factor
            vessel = vessel_segmentation.extract(slices.volume, factor)
            if (vessel[sx, sy, sz] > 0) and (vessel[tx, ty, tz] > 0):
                path = vessel_segmentation.calc_dist(vessel, sx, sy, sz, tx, ty, tz)
            if len(path) > 0:
                break
            factor *= 0.96
    if len(path) > 0:
        length = vessel_segmentation.calc_length(path, slices.spacing)
    else:
        length = -1
    result = []
    for x, y, z in path:
        result.append({
            "x": x, "y": y, "z": z,
            "sop_instance_uid": slices.mra_slices[z].SOPInstanceUID,
        })
    return json.dumps({
        "length": length,
        "path": result
    })

if __name__ == "__main__":
    app.run(port=8888)

