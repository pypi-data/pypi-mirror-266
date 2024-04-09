import warnings

import numpy as np
import blosc2
from io import BytesIO
import pickle
from pathlib import Path
from typing import Any
import awkward as ak

from numba import njit, prange

from dogma_data.utils import check_equality, timer, ceildiv
from smart_open import open as smart_open

from dogma_rust import awkward_from_list_of_numpy

# import os
# os.environ['EXTRA_CLING_ARGS'] = '-O3'

# import cppyy

# cppyy.add_include_path(np.get_include())
# cppyy.include(Path(__file__).parents[1] / "cpp_functions.hpp")


def _merge_cu_seqlens(cu_seqlens_l: list[np.ndarray]):
    i = 0
    ready_to_merge = [cu_seqlens_l[0]]
    while i < len(cu_seqlens_l) - 1:
        current = ready_to_merge[-1]
        next = cu_seqlens_l[i + 1][1:]  # Skip the first zero, since it's implied by the final element of the previous array
        ref_point = current[-1] 
        next_adjusted = next + ref_point
        ready_to_merge.append(next_adjusted)
        i += 1

    return np.concatenate(ready_to_merge)


def find_chunk_size(total_size):
    assert total_size >= 0
    # Each chunk needs to be at most 2**32 - 1, so keep dividing by 2 until we get a valid chunk size 
    current = total_size
    while current > 2**32 - 1:
        current //= 2
    return current


def _compress_leaves(node: dict | tuple | list | Any) -> dict | tuple | list | bytes:
    if isinstance(node, dict):
        return {k: _compress_leaves(v) for k, v in node.items()}
    elif isinstance(node, (tuple, list)):
        return [_compress_leaves(v) for v in node]
    elif isinstance(node, np.ndarray):
        return blosc2.pack_array2(node)
    else:
        return node

def _decompress_leaves(node: dict | tuple | list | bytes) -> dict | tuple | list | Any:
    if isinstance(node, dict):
        return {k: _decompress_leaves(v) for k, v in node.items()}
    elif isinstance(node, (tuple, list)):
        return [_decompress_leaves(v) for v in node]
    elif isinstance(node, bytes):
        return blosc2.unpack_array2(node)
    else:
        return node


def write_blosc_pickle(node: dict | tuple | list, path: Path):
    compressed = _compress_leaves(node)
    with smart_open(path, 'wb') as f:
        pickle.dump(compressed, f)

def read_blosc_pickle(path: Path) -> dict | tuple | list:
    with smart_open(path, 'rb') as f, timer('Reading blosc pickle'):
        compressed = pickle.load(f)
    with timer('Decompressing'):
        return _decompress_leaves(compressed)


def write_awkward(arr: ak.Array, path: Path | str):
    """
    Write any awkward array to file.
    Compresses the underlying buffers with Blosc2 blosclz for efficient storage and very fast reading/writing with multiple threads.
    """
    blosc2.set_nthreads(64)
    tree = ak.to_buffers(arr)
    write_blosc_pickle(tree, path)

def read_awkward(path: Path | str) -> ak.Array:
    """
    Read any awkward array from file.
    Decompresses using Blosc2 blosclz for very fast reading with multiple threads.
    """
    blosc2.set_nthreads(64)
    tree = read_blosc_pickle(path)
    return ak.from_buffers(*tree)

@njit(parallel=True)
def _fast_pack(seqlens, starts, stops, content):
    """
    Helper function to quickly pack content into a new Awkward array buffer.
    """
    cu_seqlens = np.zeros((len(seqlens) + 1,), dtype=np.int64)
    cu_seqlens[1:] = np.cumsum(seqlens)
    n_seqs = len(seqlens)
    out_size = np.sum(seqlens)
    out_arr = np.zeros((out_size,), dtype=content.dtype)
    for i in prange(n_seqs):
        start = starts[i]
        stop = stops[i]
        data = content[start:stop]
        out_arr[cu_seqlens[i]:cu_seqlens[i + 1]] = data
    return out_arr, cu_seqlens

def fast_permute_and_pack(arr: ak.Array, permutation: np.ndarray) -> ak.Array:
    """
    Index the array with the indices given by `permutation`, and pack the resulting Awkward array into contiguous buffers.

    arr: ak.Array - A RecordArray
    permutation: np.ndarray - An array of indices of the rows of the RecordArray to keep, not necessarily in order.

    Returns: ak.Array - A new RecordArray with the rows permuted and packed into contiguous buffers. Ready to write.
    """
    assert len(arr.fields) > 0
    assert isinstance(arr.layout, ak.contents.RecordArray)
    new_fields = {}
    for field_name in arr.fields:
        field = arr[field_name]
        if isinstance(field.layout, ak.contents.listoffsetarray.ListOffsetArray):
            seqlens = ak.num(field).layout.data[permutation]
            starts = field.layout.offsets[permutation].data
            stops = field.layout.offsets[permutation + 1].data
            content = field.layout.content.data
            packed_arr, cu_seqlens = _fast_pack(seqlens, starts, stops, content)
            new_field = ak.contents.ListOffsetArray(ak.index.Index64(cu_seqlens), ak.contents.NumpyArray(packed_arr))
            new_fields[field_name] = new_field
        elif isinstance(field.layout, ak.contents.NumpyArray):
            new_field = field.layout.data[permutation]
            new_fields[field_name] = ak.contents.NumpyArray(new_field)
        else:
            raise NotImplementedError(f'Cannot handle layout {field.layout}')
    return ak.Array(ak.contents.RecordArray(new_fields.values(), new_fields.keys()))
    # return ak.Array(ak.layout.ListOffsetArray64(ak.layout.Index64(new_cu_seqlens), new_content))
    

def awkward_from_flat(all_tokens: np.ndarray, cu_seqlens: np.ndarray) -> ak.Array:
    assert all_tokens.shape[0] == cu_seqlens[-1], 'Mismatched cu_seqlens and all_tokens shapes'
    assert cu_seqlens.dtype == np.int64
    if all_tokens.dtype != np.uint8:
        warnings.warn('The input tokens are not of type np.uint8. This can mean massive amounts of wasted space. Make sure this was intentional.', RuntimeWarning)
    offsets = ak.index.Index64(cu_seqlens)
    tokens = ak.contents.NumpyArray(all_tokens)
    return ak.Array(ak.contents.ListOffsetArray(offsets, tokens))



# Must be done in pure C++ because Numba cannot parallelize over elements of the Python list (due to the GIL)
# @njit(parallel=True)
# def concatenate_arrays(all_rows, cu_seqlens, all_tokens):
#     num_seq = len(all_rows)
#     num_threads = 64
#     block_size = ceildiv(num_seq, num_threads)
#     for t in prange(num_threads):
#         start_row = t * block_size
#         end_row = min((t + 1) * block_size, num_seq)
#         for i in range(start_row, end_row):
#             start = cu_seqlens[i]
#             stop = cu_seqlens[i + 1]
#             all_tokens[start:stop] = all_rows[i]

def make_random_access_buffer(all_rows: list[np.ndarray]):
    if all_rows[0].dtype != np.uint8:
        raise NotImplementedError('Only uint8 arrays are currently implemented. If you need any other types, please open an issue in the GitHub repository.')
    num_sequences = len(all_rows)
    all_tokens, cu_seqlens = concatenate_arrays(all_rows)
    assert len(cu_seqlens) == num_sequences + 1

    all_tokens = np.zeros(cu_seqlens[-1], dtype=all_rows[0].dtype)
    with timer('concat'):
        concatenate_arrays(all_rows, cu_seqlens.data, all_tokens.data)
    return all_tokens, cu_seqlens

def awkward_from_list_of_arrays(l: list[np.ndarray]) -> ak.Array:
    """
    Fast parallel implementation of concatenating lots of numpy arrays into a single packed awkward array.
    """
    all_tokens, cu_seqlens = make_random_access_buffer(l)
    return awkward_from_flat(all_tokens, cu_seqlens)




class PackedDataset:
    all_tokens: np.ndarray
    cu_seqlens: np.ndarray

    def __init__(self, all_tokens, cu_seqlens):
        self.all_tokens = all_tokens
        self.cu_seqlens = cu_seqlens
    
    # @classmethod
    # def from_h5file(cls, path):
    #     import hdf5plugin
    #     with h5py.File(path, 'r') as f:
    #         cu_seqlens = f['cu_seqlens'][:]
    #         all_tokens = f['all_tokens'][:]
    #         return cls(all_tokens, cu_seqlens)
    
    # def to_h5file(self, path):
    #     import hdf5plugin
    #     with h5py.File(path, 'w') as f:
    #         f.create_dataset('all_tokens', data=self.all_tokens, **hdf5plugin.Blosc2(), chunks=(find_chunk_size(self.all_tokens.shape[0])))
    #         f.create_dataset('cu_seqlens', data=self.cu_seqlens, **hdf5plugin.Blosc2(), chunks=(find_chunk_size(self.cu_seqlens.shape[0])))

    
    def __getitem__(self, idx):
        index = self.cu_seqlens[idx:idx+2]
        return self.all_tokens[index[0]:index[1]]
    
    def __len__(self):
        return len(self.cu_seqlens) - 1
    
    def as_awkward(self):
        import awkward as ak
        offsets = ak.index.Index64(self.cu_seqlens)
        tokens = ak.contents.NumpyArray(self.all_tokens)
        return ak.Array(ak.contents.ListOffsetArray(offsets, tokens))
    
    def seq_lens(self):
        return np.diff(self.cu_seqlens)
    
    @classmethod
    def merge_datasets(cls, datasets):
        warnings.warn('This function is deprecated. Merge the resulting awkward arrays instead.', DeprecationWarning)
        all_tokens = np.concatenate([d.all_tokens for d in datasets])
        cu_seqlens = _merge_cu_seqlens([d.cu_seqlens for d in datasets])
        assert all_tokens.shape[0] == cu_seqlens[-1]

        new_dataset = cls(all_tokens, cu_seqlens)
        assert len(new_dataset) == sum(len(d) for d in datasets)

        return new_dataset
    
    def to_file(self, path, verify_file=False):

        blosc2.set_nthreads(64)
        tokens_packed = blosc2.pack_array2(self.all_tokens)
        cu_seqlens_packed = blosc2.pack_array2(self.cu_seqlens)
        with open(path, 'wb') as f:
            pickle.dump({
                'all_tokens': tokens_packed,
                'cu_seqlens': cu_seqlens_packed
            }, f)
        if verify_file:
            with open(path, 'rb') as f:
                with timer('reading pickle'):
                    d = pickle.load(f)
                with timer('Unpacking all_tokens'):
                    all_tokens = blosc2.unpack_array2(d['all_tokens'])
                with timer('Unpacking cu_seqlens'):
                    cu_seqlens = blosc2.unpack_array2(d['cu_seqlens'])
                
                with timer('Checking equality'):
                    check_equality(all_tokens, self.all_tokens)
                    check_equality(cu_seqlens, self.cu_seqlens)

    @classmethod
    def from_file(cls, path: str | Path):
        """
        The file should be a pickle of blosc packed arrays.
        """
        blosc2.set_nthreads(64)
        with open(path, 'rb') as f:
            d = pickle.load(f)
        all_tokens = blosc2.unpack_array2(d['all_tokens'])
        cu_seqlens = blosc2.unpack_array2(d['cu_seqlens'])
        return cls(all_tokens, cu_seqlens)
