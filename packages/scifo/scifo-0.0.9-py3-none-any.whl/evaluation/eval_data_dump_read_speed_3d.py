import zarr
from imagecodecs.numcodecs import JpegXl
from numcodecs import Blosc
import numpy as np
import numcodecs
import shutil
import perfplot
from pathlib import Path
from os.path import join
import plotly.graph_objects as go
import dask.array as da
import pickle
import inspect
import random
import utils
import time
import blosc2
from collections import defaultdict
from tqdm import tqdm

numcodecs.register_codec(JpegXl)

def bench(setup, methods, n_range, repetitions): 
    timings = defaultdict(lambda: defaultdict(list))
    with tqdm(total=len(methods)*len(n_range)*repetitions) as pbar:
        for n in n_range:
            method_input = setup(n)
            for method in methods:
                for _ in range(repetitions):
                    start_time = time.time()
                    method(*method_input)
                    duration = time.time() - start_time
                    timings[method][n].append(duration)
                    pbar.update(1)
    return timings

def m_numpy_uncompressed(name):
    array = np.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.npy"))

def m_numpy_compressed(name):
    array = np.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.npz"))["array"]

def m_zarr_default(name):
    # array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), mode='r')
    # array = np.array(array_zarr)
    array = zarr.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"))

def m_zarr_uncompressed(name):
    # array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), mode='r')
    # array = np.array(array_zarr)
    array = zarr.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"))

def m_blosc2(name):
    array = blosc2.load_array(urlpath=join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.b2"))

# def m_zarr_dask_default(name):
#     dask_array = da.from_zarr(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"))
#     array = np.array(dask_array)

# def m_zarr_dask_uncompressed(name):
#     dask_array = da.from_zarr(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"))
#     array = np.array(dask_array)

def m_zarr_jpegxl_lossless(name):
    # array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), mode='r')
    # array = np.array(array_zarr)
    array = zarr.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"))

def m_zarr_jpegxl_lossy(name):
    # array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), mode='r')
    # array = np.array(array_zarr)
    array = zarr.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"))

# def m_zarr_dask_jpegxl_lossless(name):
#     dask_array = da.from_zarr(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"))
#     array = np.array(dask_array)

def m_zarr_blosc_blosclz(name):
    # array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), mode='r')
    # array = np.array(array_zarr)
    array = zarr.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"))

def m_zarr_blosc_lz4(name):
    # array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), mode='r')
    # array = np.array(array_zarr)
    array = zarr.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"))

def m_zarr_blosc_lz4hc(name):
    # array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), mode='r')
    # array = np.array(array_zarr)
    array = zarr.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"))

def m_zarr_blosc_zlib(name):
    # array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), mode='r')
    # array = np.array(array_zarr)
    array = zarr.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"))

def m_zarr_blosc_zstd(name):
    # array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), mode='r')
    # array = np.array(array_zarr)
    array = zarr.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"))

def m_zarr_zip(name):
    # array_zarr = zarr.open(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), mode='r'), mode='r')["array"]
    # array = np.array(array_zarr)
    array = zarr.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), path="array")

# def m_zarr_dask_zip(name):
#     dask_array = da.from_zarr(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), mode='r'))
#     array = np.array(dask_array)

def m_zarr_zip_uncompressed(name):
    # array_zarr = zarr.open(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), mode='r'), mode='r')["array"]
    # array = np.array(array_zarr)
    array = zarr.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), path="array")

# def m_zarr_dask_zip_uncompressed(name):
#     dask_array = da.from_zarr(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), mode='r'))
#     array = np.array(dask_array)

def m_zarr_zip_jpegxl_lossless(name):
    # array_zarr = zarr.open(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), mode='r'), mode='r')["array"]
    # array = np.array(array_zarr)
    array = zarr.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), path="array")

def m_zarr_zip_jpegxl_lossy(name):
    # array_zarr = zarr.open(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), mode='r'), mode='r')["array"]
    # array = np.array(array_zarr)
    array = zarr.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), path="array")

# def m_zarr_dask_zip_jpegxl_lossless(name):
#     dask_array = da.from_zarr(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), mode='r'))
#     array = np.array(dask_array)

# def m_zarr_dask_zip_jpegxl_lossy(name):
#     dask_array = da.from_zarr(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), mode='r'))
#     array = np.array(dask_array)

def setup(index):
    return names[index], 

def plot(methods, eval_results, title, save_filepath):
    fig = go.Figure()
    for method in methods:
        fig.add_trace(go.Scatter(x=names, y=eval_results[method.__name__], mode='lines', name=method.__name__[2:]))
    fig.update_layout(title=title, xaxis_title='Dataset', yaxis_title='Runtime [s]')
    fig.write_image(save_filepath)

if __name__ == '__main__':
    start_time = time.time()
    tmp_dir = "/home/k539i/Documents/projects/Scifo/evaluation/tmp"
    Path(tmp_dir).mkdir(parents=True, exist_ok=True)

    random.seed(2024)
    dataset_dir = "/home/k539i/Documents/datasets/original/HI_2023_ScribbleSupervision/evaluation/Dataset1200_AMOS2022_task2/imagesTr"
    names = utils.load_filenames(dataset_dir)
    random.shuffle(names)
    names = names[:100]
    n_range = range(len(names))

    methods = [globals()[name] for name in globals() if callable(globals()[name]) and name.startswith('m_')]

    timings = bench(setup, methods, n_range, 1)

    eval_results = {method.__name__: np.concatenate([list(values) for values in durations.values()]) for method, durations in timings.items()}

    # shutil.rmtree(tmp_dir)
    # shutil.rmtree("/home/k539i/Documents/network_drives/cluster-home/projects/scifo/evaluation/tmp", ignore_errors=True)

    with open('/home/k539i/Documents/projects/Scifo/evaluation/results/eval_data_dump_read_speed_3d/eval_results.pkl', 'wb') as handle:
        pickle.dump(eval_results, handle, protocol=pickle.HIGHEST_PROTOCOL)

    duration = np.round(((time.time() - start_time) / 60), 0)
    print(f"Benchmarking time: {duration}m")
