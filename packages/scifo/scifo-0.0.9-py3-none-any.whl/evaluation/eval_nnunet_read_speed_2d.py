import os
from time import time
from typing import List, Type

import numpy as np
import torch
from batchgenerators.dataloading.nondet_multi_threaded_augmenter import NonDetMultiThreadedAugmenter
from batchgenerators.transforms.utility_transforms import NumpyToTensor
from batchgenerators.utilities.file_and_folder_operations import join, load_pickle, isfile, write_pickle, subfiles, \
    load_json, maybe_mkdir_p
from nnunetv2.paths import nnUNet_preprocessed
from nnunetv2.training.dataloading.data_loader_3d import nnUNetDataLoader3D
from nnunetv2.training.dataloading.data_loader_2d import nnUNetDataLoader2D
from nnunetv2.training.dataloading.utils import get_case_identifiers, unpack_dataset
from nnunetv2.training.dataloading.nnunet_dataset import nnUNetDataset
from nnunetv2.utilities.plans_handling.plans_handler import PlansManager
from scipy.ndimage import uniform_filter1d
import blosc2
from tqdm import tqdm
from tqdmp import tqdmp
import pickle
import zarr
import utils
import numcodecs
from pathlib import Path


class nnUNetDatasetNumpy(object):
    def __init__(self, folder: str, case_identifiers: List[str] = None):
        """
        Here is some documentation, just for you
        This only abstracts the saving and loading of data so that we can experiment with different backends (npz, npy, zarr, ...)
        This is a crippled version of what is in nnU-Net -> good for experimentation
        We do not hold properties in memory and load them on the fly. Other than the default save formats should
        also be able to handle the properties!
        We don't keep files open, for now.
        self.dataset is a dictionary of case_identifier -> filename
        self.__getitem__ now loads the case. IMPORTANT! LOADING SHOULD ONLY OPEN THE FILE, NOT READ THE DATA (mmap_mode='r')
        """
        super().__init__()
        # print('loading dataset')
        if case_identifiers is None:
            case_identifiers = get_case_identifiers(folder)
        case_identifiers.sort()

        self.dataset = {}
        self.setup_dataset(folder, case_identifiers)

    def setup_dataset(self, folder, case_identifiers):
        for c in case_identifiers:
            self.dataset[c] = {}
            self.dataset[c]['data_file'] = join(folder, f"{c}.npz")
            self.dataset[c]['properties_file'] = join(folder, f"{c}.pkl")

    def __getitem__(self, key):
        entry = self.dataset[key]
        # if not isfile(entry['data_file'][:-4] + ".npy") or not isfile(entry['data_file'][:-4] + "_seg.npy"):
        #     raise RuntimeError('Unpack the dataset first with unpack_dataset')
        data = np.load(entry['data_file'][:-4] + ".npy", 'r')
        seg = np.load(entry['data_file'][:-4] + "_seg.npy", 'r')
        properties = load_pickle(entry['properties_file'])
        return data, seg, properties

    def load_case(self, key):
        """Interface required by nnUNetDataLoaderBase"""
        return self[key]

    @staticmethod
    def save_case(data: np.ndarray, seg: np.ndarray, properties: dict, output_filename: str):
        np.savez_compressed(output_filename, data=data, seg=seg)
        write_pickle(properties, output_filename + '.pkl')

    def keys(self):
        return self.dataset.keys()


class nnUNetDatasetBlosc2(object):
    def __init__(self, folder: str, case_identifiers: List[str] = None):
        """
        Here is some documentation, just for you
        This only abstracts the saving and loading of data so that we can experiment with different backends (npz, npy, zarr, ...)
        This is a crippled version of what is in nnU-Net -> good for experimentation
        We do not hold properties in memory and load them on the fly. Other than the default save formats should
        also be able to handle the properties!
        We don't keep files open, for now.
        self.dataset is a dictionary of case_identifier -> filename
        self.__getitem__ now loads the case. IMPORTANT! LOADING SHOULD ONLY OPEN THE FILE, NOT READ THE DATA (mmap_mode='r')
        """
        super().__init__()
        # print('loading dataset')
        if case_identifiers is None:
            case_identifiers = get_case_identifiers(folder)
        case_identifiers.sort()

        self.dataset = {}
        self.setup_dataset(folder, case_identifiers)

    def setup_dataset(self, folder, case_identifiers):
        for c in case_identifiers:
            self.dataset[c] = {}
            self.dataset[c]['data_file'] = join(folder, f"{c}.b2nd")
            self.dataset[c]['properties_file'] = join(folder, f"{c}.pkl")

    def __getitem__(self, key):
        entry = self.dataset[key]
        if not isfile(entry['data_file'][:-5] + ".b2nd") or not isfile(entry['data_file'][:-5] + "_seg.b2nd"):
            raise RuntimeError('Unpack the dataset first with unpack_dataset')
        data = blosc2.open(urlpath=entry['data_file'][:-5] + ".b2nd", mode='r')
        seg = blosc2.open(urlpath=entry['data_file'][:-5] + "_seg.b2nd", mode='r')
        properties = load_pickle(entry['properties_file'])
        return data, seg, properties

    def load_case(self, key):
        """Interface required by nnUNetDataLoaderBase"""
        return self[key]

    @staticmethod
    def save_case(data: np.ndarray, seg: np.ndarray, properties: dict, output_filename: str, chunks=None, blocks=None, chunks_seg=None, blocks_seg=None):
        if chunks_seg is None:
            chunks_seg = chunks
        if blocks_seg is None:
            blocks_seg = blocks
        blosc2.asarray(data, urlpath=f"{output_filename}.b2nd", chunks=chunks, blocks=blocks)
        blosc2.asarray(seg, urlpath=f"{output_filename}_seg.b2nd", chunks=chunks_seg, blocks=blocks_seg)
        write_pickle(properties, output_filename + '.pkl')

    def keys(self):
        return self.dataset.keys()
    

class nnUNetDatasetZarr(object):
    def __init__(self, folder: str, case_identifiers: List[str] = None):
        """
        Here is some documentation, just for you
        This only abstracts the saving and loading of data so that we can experiment with different backends (npz, npy, zarr, ...)
        This is a crippled version of what is in nnU-Net -> good for experimentation
        We do not hold properties in memory and load them on the fly. Other than the default save formats should
        also be able to handle the properties!
        We don't keep files open, for now.
        self.dataset is a dictionary of case_identifier -> filename
        self.__getitem__ now loads the case. IMPORTANT! LOADING SHOULD ONLY OPEN THE FILE, NOT READ THE DATA (mmap_mode='r')
        """
        super().__init__()
        # print('loading dataset')
        if case_identifiers is None:
            case_identifiers = get_case_identifiers(folder)
        case_identifiers.sort()

        self.dataset = {}
        self.setup_dataset(folder, case_identifiers)

    def setup_dataset(self, folder, case_identifiers):
        for c in case_identifiers:
            self.dataset[c] = {}
            self.dataset[c]['data_file'] = join(folder, f"{c}.zarr")
            self.dataset[c]['properties_file'] = join(folder, f"{c}.pkl")

    def __getitem__(self, key):
        entry = self.dataset[key]
        data = zarr.open(entry['data_file'][:-5] + ".zarr", mode='r')
        seg = zarr.open(entry['data_file'][:-5] + "_seg.zarr", mode='r')
        properties = load_pickle(entry['properties_file'])
        return data, seg, properties

    def load_case(self, key):
        """Interface required by nnUNetDataLoaderBase"""
        return self[key]

    @staticmethod
    def save_case(data: np.ndarray, seg: np.ndarray, properties: dict, output_filename: str, chunks=None, blocks=None):
        data_zarr = zarr.open(f"{output_filename}.zarr", shape=data.shape, chunks=chunks, dtype=data.dtype, mode='w')
        data_zarr[...] = data
        seg_zarr = zarr.open(f"{output_filename}_seg.zarr", shape=data.shape, chunks=chunks, dtype=data.dtype, mode='w')
        seg_zarr[...] = seg
        write_pickle(properties, output_filename + '.pkl')

    def keys(self):
        return self.dataset.keys()


def convert_nnunet_dataset_to_target_format(dataset: nnUNetDatasetNumpy,
                                            target_dataset_class,
                                            target_folder: str,
                                            chunks,
                                            blocks, 
                                            chunks_seg, 
                                            blocks_seg):
    """
    Target dataset is your dataset class which is derived from nnUNetDataset!
    You'll want to make this multiprocessing with tqdmp :-*

    We just load the nnUNet preprocessed data and save it with the staticmethod save_case of your target_dataset_class
    """
    maybe_mkdir_p(target_folder)
    tqdmp(convert, dataset.keys(), None, dataset=dataset, target_dataset_class=target_dataset_class, target_folder=target_folder, chunks=chunks, blocks=blocks, chunks_seg=chunks_seg, blocks_seg=blocks_seg)


def convert(k, dataset, target_dataset_class, target_folder, chunks, blocks, chunks_seg, blocks_seg):
    data, seg, properties = dataset[k]
    data = np.array(data)
    seg = np.array(seg)
    target_dataset_class.save_case(data, seg, properties, join(target_folder, k), chunks, blocks, chunks_seg, blocks_seg)


if __name__ == '__main__':
    preprocess = False
    name = "numpy"
    load_path = "/media/k539i/data/datasets/original/mzz_tests/Dataset134_DIADEM_tissue_v3"
    result_save_dir = "/home/k539i/Documents/projects/Scifo/evaluation/results/eval_nnunet_read_speed_2d"

    data_class = nnUNetDatasetBlosc2
    extension = ".b2nd"
    if "zarr_" in name:
        data_class = nnUNetDatasetZarr
        extension = ".zarr"
    elif "numpy" in name:
        data_class = nnUNetDatasetNumpy
        extension = ".npy"

    if preprocess:
            CHUNKS = (3, 1, 384, 384)
            BLOCKS = None
            CHUNKS_SEG = (1, 1, 384, 384)
            BLOCKS_SEG = None
            
            names = utils.load_filenames(join(load_path, "numpy"), extension=".npy")
            names = names[::2]
            dataset_numpy = nnUNetDatasetNumpy(join(load_path, "numpy"), names)
            convert_nnunet_dataset_to_target_format(dataset_numpy, data_class, join(load_path, name), CHUNKS, BLOCKS, CHUNKS_SEG, BLOCKS_SEG)
    else:
        # let's not let multithreading ruin our day!
        torch.set_num_threads(1)
        os.environ['OMP_NUM_THREADS'] = '1'
        blosc2.set_nthreads(1)
        numcodecs.blosc.use_threads = False

        WARMUP_STEPS = 0  # 20
        # this should be long enough to allow RAM caching to kick in
        # we want to know the speed with and without RAM caching, so measure at the start and at the end of the batches
        MEASUREMENT_STEPS = 1000 # 2000
        NUM_PROCESSES = 12
        BATCH_SIZE = 4
        PATCH_SIZE = (1, 384, 384)    

        preprocessed_data_folder = join(load_path, name)
        Path(preprocessed_data_folder).mkdir(parents=True, exist_ok=True)

        # only needed for nnUNet datasets
        # unpack_dataset(preprocessed_data_folder, unpack_segmentation=True, overwrite_existing=False, num_processes=4, verify_npy=True)

        # instantiate dataset
        # names = [i[:-5] for i in subfiles(preprocessed_data_folder, suffix='.b2nd', join=False) if "_seg" not in i]
        names = utils.load_filenames(preprocessed_data_folder, extension=extension)
        names = names[::2]
        ds = data_class(preprocessed_data_folder, names)
        # now the dataloader
        plans_manager = PlansManager(join(load_path, 'nnUNetPlans.json'))
        dl = nnUNetDataLoader3D(
            ds,
            batch_size=BATCH_SIZE,
            patch_size=PATCH_SIZE,
            final_patch_size=PATCH_SIZE,
            label_manager=plans_manager.get_label_manager(load_json(join(load_path, 'dataset.json'))),
            oversample_foreground_percent=0.3,
            sampling_probabilities=None,
            pad_sides=None,
            probabilistic_oversampling=True
        )
        # wrap in multiprocessing
        mt_dl = NonDetMultiThreadedAugmenter(dl, transform=NumpyToTensor(keys=['data', 'seg']), num_processes=NUM_PROCESSES,
                                            num_cached=16, pin_memory=True, wait_time=0.001)

        #### Benchmark ####
        # start mt and let it do its thing
        for _ in range(WARMUP_STEPS):
            tmp = next(mt_dl)

        start = time()
        times = []
        for _ in tqdm(range(MEASUREMENT_STEPS)):
            st = time()
            _ = next(mt_dl)
            times.append(time() - st)
        end = time()

        # the plot is ugly AF, this is just a PoC
        import matplotlib.pyplot as plt

        y = 1 / uniform_filter1d(np.array(times), size=51)
        plt.plot(list(range(len(times))), y)
        plt.title(f'Throughput ({name}_s{MEASUREMENT_STEPS}_n{NUM_PROCESSES}_b{BATCH_SIZE}_p{PATCH_SIZE})')
        plt.xlabel('Batch')
        plt.ylabel('Throughput (batch/s)')
        # plt.ylim((0, np.max(y) * 1.1))
        plt.ylim(0, 10)
        # plt.show()

        Path(result_save_dir).mkdir(parents=True, exist_ok=True)

        with open(f'{result_save_dir}/{name}_s{MEASUREMENT_STEPS}_n{NUM_PROCESSES}_b{BATCH_SIZE}_p{PATCH_SIZE}.pkl', 'wb') as handle:
            pickle.dump({"x": list(range(len(times))), "y": y, "config": {"name": name, "WARMUP_STEPS": WARMUP_STEPS, "MEASUREMENT_STEPS": MEASUREMENT_STEPS, 
                                                                        "NUM_PROCESSES": NUM_PROCESSES, "BATCH_SIZE": BATCH_SIZE, "PATCH_SIZE": PATCH_SIZE}}, handle, protocol=pickle.HIGHEST_PROTOCOL)

        plt.savefig(f'{result_save_dir}/{name}_s{MEASUREMENT_STEPS}_n{NUM_PROCESSES}_b{BATCH_SIZE}_p{PATCH_SIZE}.png')

        print('throughput batches/s at start', 1 / np.mean(times[:(MEASUREMENT_STEPS // 4)]))
        print('throughput batches/s at end', 1 / np.mean(times[MEASUREMENT_STEPS // 4 * 3:]))
        print('throughput batches/s overall', 1 / np.mean(times))
        print(f'It took {end - start} s to load {MEASUREMENT_STEPS} batches')


