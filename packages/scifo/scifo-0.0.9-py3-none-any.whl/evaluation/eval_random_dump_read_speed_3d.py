import zarr
from imagecodecs.numcodecs import JpegXl
from numcodecs import Blosc
import numpy as np
import numcodecs
import shutil
import perfplot
from pathlib import Path
from os.path import join
import uuid
import plotly.graph_objects as go
import dask.array as da
import pickle
import inspect
from collections import defaultdict
import time

numcodecs.register_codec(JpegXl)

def m_numpy_uncompressed(array_size, chunk_size):
    array = np.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.npy"))

def m_numpy_compressed(array, chunk_size):
    array = np.load(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.npz"))["array"]

def m_zarr_default(array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r')
    array = np.array(array_zarr)

def m_zarr_uncompressed(array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r')
    array = np.array(array_zarr)

def m_zarr_dask_default(array, chunk_size):
    dask_array = da.from_zarr(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"))
    array = np.array(dask_array)

def m_zarr_dask_uncompressed(array, chunk_size):
    dask_array = da.from_zarr(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"))
    array = np.array(dask_array)

def m_zarr_jpegxl_lossless(array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r')
    array = np.array(array_zarr)

def m_zarr_jpegxl_lossy(array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r')
    array = np.array(array_zarr)

def m_zarr_dask_jpegxl_lossless(array, chunk_size):
    dask_array = da.from_zarr(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"))
    array = np.array(dask_array)

def m_zarr_blosc_blosclz(array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r')
    array = np.array(array_zarr)

def m_zarr_blosc_lz4(array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r')
    array = np.array(array_zarr)

def m_zarr_blosc_lz4hc(array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r')
    array = np.array(array_zarr)

def m_zarr_blosc_zlib(array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r')
    array = np.array(array_zarr)

def m_zarr_blosc_zstd(array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r')
    array = np.array(array_zarr)

def m_zarr_zip(array, chunk_size):
    array_zarr = zarr.open(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r'), mode='r')["array"]
    array = np.array(array_zarr)

# def m_zarr_dask_zip(array, chunk_size):
#     dask_array = da.from_zarr(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r'))
#     array = np.array(dask_array)

def m_zarr_zip_uncompressed(array, chunk_size):
    array_zarr = zarr.open(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r'), mode='r')["array"]
    array = np.array(array_zarr)

# def m_zarr_dask_zip_uncompressed(array, chunk_size):
#     dask_array = da.from_zarr(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r'))
#     array = np.array(dask_array)

def m_zarr_zip_jpegxl_lossless(array, chunk_size):
    array_zarr = zarr.open(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r'), mode='r')["array"]
    array = np.array(array_zarr)

def m_zarr_zip_jpegxl_lossy(array, chunk_size):
    array_zarr = zarr.open(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r'), mode='r')["array"]
    array = np.array(array_zarr)

# def m_zarr_dask_zip_jpegxl_lossless(array, chunk_size):
#     dask_array = da.from_zarr(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r'))
#     array = np.array(dask_array)

# def m_zarr_dask_zip_jpegxl_lossy(array, chunk_size):
#     dask_array = da.from_zarr(zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array_size[0]}.zarr"), mode='r'))
#     array = np.array(dask_array)

def setup(array_size):
    chunk_size = [array_chunk_mapping[array_size]] * 3
    return array_size, chunk_size

def plot(methods, eval_results, title, save_filepath):
    fig = go.Figure()
    for method in methods:
        fig.add_trace(go.Scatter(x=array_size, y=eval_results[method.__name__], mode='lines', name=method.__name__[2:]))
    fig.update_layout(title=title, xaxis_title='Image Size', yaxis_title='Runtime [s]')
    fig.write_image(save_filepath)

if __name__ == '__main__':
    start_time = time.time()
    tmp_dir = "/home/k539i/Documents/projects/Scifo/evaluation/tmp"
    Path(tmp_dir).mkdir(parents=True, exist_ok=True)

    repetitions = 5
    multiplier = 5
    chunk_size = np.array([(2**k) for k in range(4, 9)])
    array_size = chunk_size * 5
    array_chunk_mapping = {a_s: c_s for a_s, c_s in zip(array_size, chunk_size)}

    methods = [globals()[name] for name in globals() if callable(globals()[name]) and name.startswith('m_')]

    eval_results = defaultdict(list)

    for _ in range(repetitions):

        b = perfplot.bench(
            setup=setup,
            kernels=methods,
            title="3D random dump read speed comparison",
            n_range=array_size,
            xlabel="Image Size",
            equality_check=None,
        )

        for method, method_runtime in zip(methods, b.timings_s):
            eval_results[method.__name__].append(method_runtime)

    eval_results = {key: np.mean(value, axis=0) for key, value in eval_results.items()}

    with open('/home/k539i/Documents/projects/Scifo/evaluation/results/eval_random_dump_read_speed_3d/eval_results.pkl', 'wb') as handle:
        pickle.dump(eval_results, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    duration = np.round(((time.time() - start_time) / 60), 0)
    print(f"Benchmarking time: {duration}m")
