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
import blosc2

numcodecs.register_codec(JpegXl)

def bench(setup, methods, n_range, repetitions):


def m_numpy_uncompressed(array, chunk_size):
    np.save(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.npy"), array)

def m_numpy_compressed(array, chunk_size):
    np.savez_compressed(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.npz"), array=array)

def m_zarr_default(array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w')
    array_zarr[...] = array

def m_zarr_uncompressed(array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=None)
    array_zarr[...] = array

def m_blosc2(array, chunk_size):
    print(np.prod(chunk_size))
    blosc2.save_array(array, urlpath=join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.b2"), chunksize=np.prod(chunk_size) * array.dtype.itemsize)
    print("LOLLLLLL")

def m_zarr_dask_default(array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w')
    dask_array = da.from_array(array, chunks=chunk_size)
    da.store(dask_array, array_zarr)

def m_zarr_dask_uncompressed(array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=None)
    dask_array = da.from_array(array, chunks=chunk_size)
    da.store(dask_array, array_zarr)

def m_zarr_jpegxl_lossless(array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=JpegXl(lossless=True))
    array_zarr[...] = array

def m_zarr_jpegxl_lossy(array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=JpegXl(lossless=False))
    array_zarr[...] = array

def m_zarr_dask_jpegxl_lossless(array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=JpegXl(lossless=True))
    dask_array = da.from_array(array, chunks=chunk_size)
    da.store(dask_array, array_zarr)

def m_zarr_blosc_blosclz(array, chunk_size):
    compressor = Blosc('blosclz')
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=compressor)
    array_zarr[...] = array

def m_zarr_blosc_lz4(array, chunk_size):
    compressor = Blosc('lz4')
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=compressor)
    array_zarr[...] = array

def m_zarr_blosc_lz4hc(array, chunk_size):
    compressor = Blosc('lz4hc')
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=compressor)
    array_zarr[...] = array

def m_zarr_blosc_zlib(array, chunk_size):
    compressor = Blosc('zlib')
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=compressor)
    array_zarr[...] = array

def m_zarr_blosc_zstd(array, chunk_size):
    compressor = Blosc('zstd')
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=compressor)
    array_zarr[...] = array

def m_zarr_zip(array, chunk_size):
    zip_store = zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), compression=0, mode='w')
    grp = zarr.group(zip_store)
    grp.create_dataset("array", data=array, chunks=chunk_size, dtype=array.dtype)
    zip_store.close()

def m_zarr_dask_zip(array, chunk_size):
    array_zarr = zarr.create(shape=array.shape, chunks=chunk_size, dtype=array.dtype, store=zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), compression=0, mode='w'))
    dask_array = da.from_array(array, chunks=chunk_size)
    da.store(dask_array, array_zarr)

def m_zarr_zip_uncompressed(array, chunk_size):
    zip_store = zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), compression=0, mode='w')
    grp = zarr.group(zip_store)
    grp.create_dataset("array", data=array, chunks=chunk_size, dtype=array.dtype, compressor=None)
    zip_store.close()

def m_zarr_dask_zip_uncompressed(array, chunk_size):
    array_zarr = zarr.create(shape=array.shape, chunks=chunk_size, dtype=array.dtype, compression=None, store=zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), compression=0, mode='w'))
    dask_array = da.from_array(array, chunks=chunk_size)
    da.store(dask_array, array_zarr)

def m_zarr_zip_jpegxl_lossless(array, chunk_size):
    zip_store = zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), compression=0, mode='w')
    grp = zarr.group(zip_store)
    grp.create_dataset("array", data=array, chunks=chunk_size, dtype=array.dtype, compressor=JpegXl(lossless=True))
    zip_store.close()

def m_zarr_zip_jpegxl_lossy(array, chunk_size):
    zip_store = zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), compression=0, mode='w')
    grp = zarr.group(zip_store)
    grp.create_dataset("array", data=array, chunks=chunk_size, dtype=array.dtype, compressor=JpegXl(lossless=False))
    zip_store.close()

def m_zarr_dask_zip_jpegxl_lossless(array, chunk_size):
    array_zarr = zarr.create(shape=array.shape, chunks=chunk_size, dtype=array.dtype, compressor=JpegXl(lossless=True), store=zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), compression=0, mode='w'))
    dask_array = da.from_array(array, chunks=chunk_size)
    da.store(dask_array, array_zarr)

def m_zarr_dask_zip_jpegxl_lossy(array, chunk_size):
    array_zarr = zarr.create(shape=array.shape, chunks=chunk_size, dtype=array.dtype, compressor=JpegXl(lossless=False), store=zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{array.shape[0]}.zarr"), compression=0, mode='w'))
    dask_array = da.from_array(array, chunks=chunk_size)
    da.store(dask_array, array_zarr)

def setup(array_size):
    array = np.random.random(tuple([array_size] * 3)).astype(np.float32)
    chunk_size = [array_chunk_mapping[array_size]] * 3
    return array, chunk_size

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

    for r in range(repetitions):

        print("TMP")
        b = perfplot.bench(
            setup=setup,
            kernels=methods,
            title="3D random dump write speed comparison",
            n_range=array_size,
            xlabel="Image Size",
            equality_check=None,
        )

        for method, method_runtime in zip(methods, b.timings_s):
            eval_results[method.__name__].append(method_runtime)

        if r < repetitions-1:
            shutil.rmtree(tmp_dir)
            # shutil.rmtree("/home/k539i/Documents/network_drives/cluster-home/projects/scifo/evaluation/tmp", ignore_errors=True)

    eval_results = {key: np.mean(value, axis=0) for key, value in eval_results.items()}
    eval_results = {"x": array_size, "y": eval_results}

    with open('/home/k539i/Documents/projects/Scifo/evaluation/results/eval_random_dump_write_speed_3d/eval_results.pkl', 'wb') as handle:
        pickle.dump(eval_results, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    duration = np.round(((time.time() - start_time) / 60), 0)
    print(f"Benchmarking time: {duration}m")
