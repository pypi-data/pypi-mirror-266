from typing import Any

import numba as nb
from numba.typed import List
import awkward as ak
import numpy as np
from dogma_data.utils import ceildiv
import dogma_rust


# @nb.njit(fastmath=True)
# def _parse_fasta_line(line: str, out_view: np.ndarray, mappings: np.ndarray):
#     for i, c in enumerate(line):
#         if c == 'A':
#             out_view[i] = mappings[0]
#         elif c == 'T':
#             out_view[i] = mappings[1]
#         elif c == 'C':
#             out_view[i] = mappings[2]
#         elif c == 'G':
#             out_view[i] = mappings[3]
#         elif c == 'U' or c == 'R' or c == 'Y' or c == 'K' or c == 'M' or c == 'S' or c == 'W' or c == 'B' or c == 'D' or c == 'H' or c == 'V' or c == 'N':
#             out_view[i] = mappings[4]
#         else:
#             out_view[i] = mappings[4]
#         # else:
#         #     raise ValueError(f"Invalid character {c} in fasta sequence")

# @nb.njit(parallel=True, fastmath=True)
# def _parse_fasta(complete_file: str, mappings: np.ndarray):
#     to_next_line = False
#     # [(start_file_index, end_file_index, cu_buffer_idx)]
#     # First find all the sequences to parse
#     total_len = len(complete_file)
#     n_threads = nb.config.NUMBA_DEFAULT_NUM_THREADS
#     if len(complete_file) < 10_000:
#         n_threads = 1
#     chunk_size = ceildiv(total_len, n_threads)

#     thread_buffer_sizes = [0 for _ in range(n_threads)]
#     thread_cu_seqlenss = List(nb.int64[:, :])# [np.array([], dtype=np.int64) for _ in range(n_threads)]
#     for _ in range(n_threads):
#         thread_cu_seqlenss.append(np.array([1, 2], dtype=np.int64))

#     for t in nb.prange(n_threads):
#         start_idx = t * chunk_size
#         end_idx = min((t + 1) * chunk_size, total_len)
#         while complete_file[start_idx] != '>':  # Scan until the first header
#             start_idx += 1
#         if t != n_threads - 1:
#             while complete_file[end_idx] != '>':  # Scan until the next header or until end of file
#                 if end_idx == total_len - 1:
#                     break
#                 end_idx += 1
            
#         thread_out_sequences = List()
#         thread_buffer_size = 0

#         current_start = 0
#         for i in range(start_idx, end_idx):
#             c = complete_file[i]
#             if to_next_line:
#                 if c == '\n' or i == len(complete_file) - 1:
#                     if current_start != -1:
#                         thread_out_sequences.append((current_start, i, thread_buffer_size))
#                         thread_buffer_size += i - current_start
#                     to_next_line = False
#                 continue
#             if c == '>':
#                 # Potentially parse the header
#                 to_next_line = True
#                 current_start = -1
#                 continue
#             else:
#                 current_start = i
#                 to_next_line = True

#         out_buffer = np.zeros(thread_buffer_size, dtype=np.uint8)
#         seqlens = np.zeros(len(thread_out_sequences), dtype=np.int64)
#         for i in nb.prange(len(thread_out_sequences)):
#             start, end, buffer_start = thread_out_sequences[i]
#             _parse_fasta_line(complete_file[start:end], out_buffer[buffer_start:buffer_start + end - start], mappings)
#             seqlens[i] = end - start

#         thread_cu_seqlenss[t] = np.zeros(len(thread_out_sequences) + 1, dtype=np.int64)
#         thread_cu_seqlenss[t][1:] = np.cumsum(seqlens)
    
#     print('Stitching cu_seqlens')
#     for t in range(n_threads):
#         thread_cu_seqlenss[t] += thread_cu_seqlenss[t - 1][-1]
    
#     cu_seqlens = np.zeros(thread_cu_seqlenss[-1][-1], dtype=np.int64)
#     # for t in nb.prange(n_threads):
#     #     cu_seqlens[thread_cu_seqlenss[t]] = thread_cu_seqlenss[t][1:]


    
#     # return out_buffer, cu_seqlens
#     return thread_cu_seqlenss[-1]

# def parse_fasta(complete_file_text: str, vocab: Any) -> ak.Array:
#     """
#     complete_file_text: The entire contents of a fasta file as a string, including newlines
#     vocab: The vocabulary to use for parsing the fasta file, must contain the tokens 'a', 't', 'c', 'g', and '<unk>'
#     """
#     # Only parsing ATCG, which are lowercase in the vocab
#     mapping_values = [*[vocab[token] for token in ['a', 't', 'c', 'g']], vocab['<unk>']]
#     for val in mapping_values:
#         assert val < 256, 'Must fit in a uint8'
#     mappings = np.array(mapping_values, dtype=np.uint8)
#     buffer, cu_seqlens = _parse_fasta(complete_file_text, mappings)

#     offsets = ak.index.Index64(cu_seqlens)
#     tokens = ak.contents.NumpyArray(buffer)
#     return ak.Array(ak.contents.ListOffsetArray(offsets, tokens))
    

def parse_fasta(path: str, vocab: Any) -> ak.Array:
    """
    complete_file_text: The entire contents of a fasta file as a string, including newlines
    vocab: The vocabulary to use for parsing the fasta file, must contain the tokens 'a', 't', 'c', 'g', and '<unk>'
    """
    # Only parsing ATCG, which are lowercase in the vocab
    mapping_values = [*[vocab[token] for token in ['a', 't', 'c', 'g']], vocab['<unk>']]

    buffer, cu_seqlens,  = dogma_rust.parse_fasta(path, np.array(mapping_values, dtype=np.uint8))

    offsets = ak.index.Index64(cu_seqlens)
    tokens = ak.contents.NumpyArray(buffer)
    return ak.Array(ak.contents.ListOffsetArray(offsets, tokens))
    


if __name__ == '__main__':
    from torchtext import vocab
    from collections import OrderedDict
    AA_VOCAB = vocab.vocab(
        OrderedDict(
            [
                (token, 1)
                for token in [
                    "a", "g", "c", "t",
                    # Amino acids
                    "A",
                    "C",
                    "D",
                    "E",
                    "F",
                    "G",
                    "H",
                    "I",
                    "K",
                    "L",
                    "M",
                    "N",
                    "P",
                    "Q",
                    "R",
                    "S",
                    "T",
                    "V",
                    "W",
                    "Y",
                    "<stop>",  # Both selenocysteine and pyrrolysine
                    "<aaunk>",

                    "<rna_mask>",
                    "<aa_mask>",
                    # Indicators of the type of masking used in the sequence
                    "<seq_triple_masked>",
                    "<seq_third_masked>",
                    "<seq_rna_masked>",
                    "<seq_protein_masked>",
                ]
            ]
        ),
        specials=["<pad>", "<sos>", "<eos>", "<unk>"],
    )
    AA_VOCAB.set_default_index(AA_VOCAB["<aaunk>"])
    fasta_lines = parse_fasta('fasta_data/result_rep_seq.fasta', AA_VOCAB)
    # with open('fasta_data/result_rep_seq.fasta', 'r') as f:
    #     fasta_lines = parse_fasta(f.read(), AA_VOCAB)
    print(fasta_lines)
    breakpoint()
