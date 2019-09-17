import re
import numpy as np
import dicom
import scipy.ndimage

class MRASlices(object):
    def __init__(self, dicom_fpath_list, series_descriptions=None):
        self.dicom_fpath_list = dicom_fpath_list
        self.series_descriptions = series_descriptions
        self.mra_slices, self.mra_fpath_list = read_mra_slices(dicom_fpath_list, series_descriptions)
        self.series_id = self.mra_slices[0].SeriesInstanceUID
        self.volume = construct_volume(self.mra_slices)
        self.spacing = np.array(self.mra_slices[0].PixelSpacing + [self.mra_slices[0].SliceThickness], dtype=np.float32)

def is_mra_slice(ds, series_descriptions=None):
    return (series_descriptions is None) or (re.match("(%s)" % series_descriptions, ds.SeriesDescription))

def read_mra_slices(dicom_fpath_list, series_descriptions=None):
    res = []
    for fpath in dicom_fpath_list:
        ds = dicom.read_file(fpath)
        if is_mra_slice(ds, series_descriptions):
            res.append((ds, fpath))
    res.sort(key=lambda x: x[0].ImagePositionPatient[2])
    if len(res) > 1:
        slice_thickness = np.abs(res[0][0].SliceLocation - res[1][0].SliceLocation)
    else:
        slice_thickness = -1
    for s, _ in res:
        s.SliceThickness = slice_thickness
    mra_slices, mra_fpath_list = [ds for ds, fpath in res], [fpath for ds, fpath in res]
    return mra_slices, mra_fpath_list

def construct_volume(mra_slices):
    volume = []
    for s in mra_slices:
        volume.append(s.pixel_array)
    volume = np.asarray(volume, dtype=np.int16)
    volume = np.transpose(volume, (2, 1, 0))
    return volume


