import zarr
import numpy as np
from imagecodecs.numcodecs import JpegXl
import numcodecs
import dask.array as da

numcodecs.register_codec(JpegXl)

array_size = (100, 100, 100)
chunk_size = (10, 10, 10)
array = np.random.random(array_size).astype(np.float32)
array_zarr = zarr.create(shape=array.shape, chunks=chunk_size, dtype=array.dtype, compressor=JpegXl(lossless=True), store=zarr.ZipStore("tmp.zarr", compression=0, mode='w'))
dask_array = da.from_array(array, chunks=chunk_size)
da.store(dask_array, array_zarr)