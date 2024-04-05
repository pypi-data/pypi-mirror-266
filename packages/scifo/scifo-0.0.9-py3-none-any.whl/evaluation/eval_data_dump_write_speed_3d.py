import zarr
from imagecodecs.numcodecs import JpegXl  # , Heif
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
# numcodecs.register_codec(Heif)

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


def m_numpy_uncompressed(name, array, chunk_size):
    np.save(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.npy"), array)

def m_numpy_compressed(name, array, chunk_size):
    np.savez_compressed(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.npz"), array=array)

def m_zarr_default(name, array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w')
    array_zarr[...] = array
    # zarr.save(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), array, chunks=chunk_size)

def m_zarr_uncompressed(name, array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=None)
    array_zarr[...] = array

def m_blosc2(name, array, chunk_size):
    chunk_size_tmp = chunk_size
    if not chunk_size:
        chunk_size_tmp = array.shape
    blosc2.save_array(array, urlpath=join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.b2"), chunksize=np.prod(chunk_size_tmp) * array.dtype.itemsize)

# def m_zarr_dask_default(name, array, chunk_size):
#     # print(f"{inspect.currentframe().f_code.co_name}: {name}")
#     array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w')
#     dask_array = da.from_array(array, chunks=chunk_size)
#     da.store(dask_array, array_zarr)

# def m_zarr_dask_uncompressed(name, array, chunk_size):
#     # print(f"{inspect.currentframe().f_code.co_name}: {name}")
#     array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=None)
#     dask_array = da.from_array(array, chunks=chunk_size)
#     da.store(dask_array, array_zarr)

def m_zarr_jpegxl_lossless(name, array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=JpegXl(lossless=True))
    array_zarr[...] = array

def m_zarr_jpegxl_lossy(name, array, chunk_size):
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=JpegXl(lossless=False))
    array_zarr[...] = array

# def m_zarr_dask_jpegxl_lossless(name, array, chunk_size):
#     array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=JpegXl(lossless=True))
#     dask_array = da.from_array(array, chunks=chunk_size)
#     da.store(dask_array, array_zarr)

def m_zarr_blosc_blosclz(name, array, chunk_size):
    compressor = Blosc('blosclz')
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=compressor)
    array_zarr[...] = array

def m_zarr_blosc_lz4(name, array, chunk_size):
    compressor = Blosc('lz4')
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=compressor)
    array_zarr[...] = array

def m_zarr_blosc_lz4hc(name, array, chunk_size):
    compressor = Blosc('lz4hc')
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=compressor)
    array_zarr[...] = array

def m_zarr_blosc_zlib(name, array, chunk_size):
    compressor = Blosc('zlib')
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=compressor)
    array_zarr[...] = array

def m_zarr_blosc_zstd(name, array, chunk_size):
    compressor = Blosc('zstd')
    array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=compressor)
    array_zarr[...] = array

# def m_zarr_heif(name, array, chunk_size):
#     array_zarr = zarr.open(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zarr"), shape=array.shape, chunks=chunk_size, dtype=array.dtype, mode='w', compressor=Heif())
#     array_zarr[...] = array

def m_zarr_zip(name, array, chunk_size):
    zip_store = zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), compression=0, mode='w')
    grp = zarr.group(zip_store)
    grp.create_dataset("array", data=array, chunks=chunk_size, dtype=array.dtype)
    zip_store.close()

# def m_zarr_dask_zip(name, array, chunk_size):
#     array_zarr = zarr.create(shape=array.shape, chunks=chunk_size, dtype=array.dtype, store=zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), compression=0, mode='w'))
#     dask_array = da.from_array(array, chunks=chunk_size)
#     da.store(dask_array, array_zarr)

def m_zarr_zip_uncompressed(name, array, chunk_size):
    zip_store = zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), compression=0, mode='w')
    grp = zarr.group(zip_store)
    grp.create_dataset("array", data=array, chunks=chunk_size, dtype=array.dtype, compressor=None)
    zip_store.close()

# def m_zarr_dask_zip_uncompressed(name, array, chunk_size):
#     array_zarr = zarr.create(shape=array.shape, chunks=chunk_size, dtype=array.dtype, compression=None, store=zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), compression=0, mode='w'))
#     dask_array = da.from_array(array, chunks=chunk_size)
#     da.store(dask_array, array_zarr)

def m_zarr_zip_jpegxl_lossless(name, array, chunk_size):
    zip_store = zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), compression=0, mode='w')
    grp = zarr.group(zip_store)
    grp.create_dataset("array", data=array, chunks=chunk_size, dtype=array.dtype, compressor=JpegXl(lossless=True))
    zip_store.close()

def m_zarr_zip_jpegxl_lossy(name, array, chunk_size):
    zip_store = zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), compression=0, mode='w')
    grp = zarr.group(zip_store)
    grp.create_dataset("array", data=array, chunks=chunk_size, dtype=array.dtype, compressor=JpegXl(lossless=False))
    zip_store.close()

# def m_zarr_dask_zip_jpegxl_lossless(name, array, chunk_size):
#     array_zarr = zarr.create(shape=array.shape, chunks=chunk_size, dtype=array.dtype, compressor=JpegXl(lossless=True), store=zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), compression=0, mode='w'))
#     dask_array = da.from_array(array, chunks=chunk_size)
#     da.store(dask_array, array_zarr)

# def m_zarr_dask_zip_jpegxl_lossy(name, array, chunk_size):
#     array_zarr = zarr.create(shape=array.shape, chunks=chunk_size, dtype=array.dtype, compressor=JpegXl(lossless=False), store=zarr.ZipStore(join(tmp_dir, f"{inspect.currentframe().f_code.co_name}_{name}.zip"), compression=0, mode='w'))
#     dask_array = da.from_array(array, chunks=chunk_size)
#     da.store(dask_array, array_zarr)

def setup(index):
    array = utils.load_nifti(join(dataset_dir, f"{names[index]}.nii.gz")).astype(np.float32)
    return names[index], array, False

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

    with open('/home/k539i/Documents/projects/Scifo/evaluation/results/eval_data_dump_write_speed_3d/eval_results.pkl', 'wb') as handle:
        pickle.dump(eval_results, handle, protocol=pickle.HIGHEST_PROTOCOL)

    duration = np.round(((time.time() - start_time) / 60), 0)
    print(f"Benchmarking time: {duration}m")
