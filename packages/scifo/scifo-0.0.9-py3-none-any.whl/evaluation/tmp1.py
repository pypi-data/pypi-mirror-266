import blosc2
import numpy as np
import os

array = np.random.random((5,)).astype(np.float32)
print("itemsize: ", array.dtype.itemsize)
print("array1: ", array)
blosc2.save_array(array, urlpath="tmp.b2", chunksize=np.prod(1)*array.dtype.itemsize)
array = blosc2.load_array("tmp.b2")
print("array2: ", array)
os.remove("tmp.b2")

# TODO: How to get byte size of dtype? Divide by 8 as float32 is in bits. arr.itemsize ?