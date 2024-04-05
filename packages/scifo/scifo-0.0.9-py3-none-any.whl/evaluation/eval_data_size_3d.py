import zarr
import numpy as np
from pathlib import Path
from os.path import join
import pickle
import inspect
import random
import utils
import time
import os
import blosc2

def get_dir_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

def m_numpy_uncompressed(name):
    return os.path.getsize(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.npy")) / 1014 / 1014

def m_numpy_compressed(name):
    return os.path.getsize(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.npz")) / 1014 / 1014

def m_zarr_default(name):
    return get_dir_size(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr")) / 1014 / 1014

def m_zarr_uncompressed(name):
    return get_dir_size(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr")) / 1014 / 1014

def m_blosc2(name):
    return os.path.getsize(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.b2")) / 1014 / 1014

# def m_zarr_dask_default(name):
#     dask_array = da.from_zarr(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"))
#     array = np.array(dask_array)

# def m_zarr_dask_uncompressed(name):
#     dask_array = da.from_zarr(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"))
#     array = np.array(dask_array)

def m_zarr_jpegxl_lossless(name):
    return get_dir_size(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr")) / 1014 / 1014

def m_zarr_jpegxl_lossy(name):
    return get_dir_size(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr")) / 1014 / 1014

# def m_zarr_dask_jpegxl_lossless(name):
#     dask_array = da.from_zarr(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"))
#     array = np.array(dask_array)

def m_zarr_blosc_blosclz(name):
    return get_dir_size(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr")) / 1014 / 1014

def m_zarr_blosc_lz4(name):
    return get_dir_size(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr")) / 1014 / 1014

def m_zarr_blosc_lz4hc(name):
    return get_dir_size(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr")) / 1014 / 1014

def m_zarr_blosc_zlib(name):
    return get_dir_size(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr")) / 1014 / 1014

def m_zarr_blosc_zstd(name):
    return get_dir_size(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr")) / 1014 / 1014

def m_zarr_zip(name):
    return os.path.getsize(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip")) / 1014 / 1014

# def m_zarr_dask_zip(name):
#     dask_array = da.from_zarr(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), mode='r'))
#     array = np.array(dask_array)

def m_zarr_zip_uncompressed(name):
    return os.path.getsize(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip")) / 1014 / 1014

# def m_zarr_dask_zip_uncompressed(name):
#     dask_array = da.from_zarr(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), mode='r'))
#     array = np.array(dask_array)

def m_zarr_zip_jpegxl_lossless(name):
    return os.path.getsize(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip")) / 1014 / 1014

def m_zarr_zip_jpegxl_lossy(name):
    return os.path.getsize(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip")) / 1014 / 1014

# def m_zarr_dask_zip_jpegxl_lossless(name):
#     dask_array = da.from_zarr(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), mode='r'))
#     array = np.array(dask_array)

# def m_zarr_dask_zip_jpegxl_lossy(name):
#     dask_array = da.from_zarr(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), mode='r'))
#     array = np.array(dask_array)

if __name__ == '__main__':
    start_time = time.time()
    tmp_dir = "/home/k539i/Documents/projects/Scifo/evaluation/tmp"
    Path(tmp_dir).mkdir(parents=True, exist_ok=True)

    random.seed(2024)
    dataset_dir = "/home/k539i/Documents/datasets/original/HI_2023_ScribbleSupervision/evaluation/Dataset1200_AMOS2022_task2/imagesTr"
    names = utils.load_filenames(dataset_dir)
    random.shuffle(names)
    names = names[:100]

    methods = [globals()[name] for name in globals() if callable(globals()[name]) and name.startswith('m_')]

    eval_results = {method.__name__: [method(name) for name in names] for method in methods}

    with open('/home/k539i/Documents/projects/Scifo/evaluation/results/eval_data_size_3d/eval_results.pkl', 'wb') as handle:
        pickle.dump(eval_results, handle, protocol=pickle.HIGHEST_PROTOCOL)

    duration = np.round(((time.time() - start_time) / 60), 0)
    print(f"Benchmarking time: {duration}m")
