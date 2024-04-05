import numpy as np
import h5py
import os

def read_hdf5(filename):
    """
    ....
    """
    with h5py.File(filename, 'r') as h5file:
        return recursively_load_dict_contents_from_group(h5file, '/')

def recursively_load_dict_contents_from_group(h5file, path):
    """
    ....
    """
    ans = {}
    for i in h5file[path].attrs.keys():
        ans[i] = h5file[path].attrs[i]
    for key, item in h5file[path].items():
        
        if isinstance(item, h5py._hl.dataset.Dataset):
            ans[key] = item[...]
        if isinstance(item, h5py._hl.group.Group):
            ans[key] = recursively_load_dict_contents_from_group(h5file, path + key + '/')
           
    return ans