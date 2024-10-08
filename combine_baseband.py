#!/usr/bin/env python

import os
import mmap
import time
from tqdm import tqdm
from multiprocessing import Process
from args_parser import parse_args_deal_baseband

def memory_map_read(filename, access=mmap.ACCESS_READ):
    size = os.path.getsize(filename)
    fd = os.open(filename, os.O_RDONLY)
    return mmap.mmap(fd, size, access=access), size

def memory_map_write(filename, size, access=mmap.ACCESS_WRITE):
    with open(filename, 'wb') as f:
        f.seek(size - 1)
        f.write(b'\x00')
    fd = os.open(filename, os.O_RDWR)
    return mmap.mmap(fd, size, access=access)

def process_chunk(in1, in2, out, start, chunk_size):
    out[2 * start:2 * start + chunk_size] = in1[start:start + chunk_size]
    out[2 * start + chunk_size:2 * (start + chunk_size)] = in2[start:start + chunk_size]

def combine_baseband(file1, file2, outfile, chunk_size, num_processes):
    in1, size1 = memory_map_read(file1)
    in2, size2 = memory_map_read(file2)
    size = size1  # Assume both files have the same size

    # Create empty output file
    out = memory_map_write(outfile, 2 * size)

    processes = []
    for i in tqdm(range(0, size, chunk_size), desc="Processing", unit="blocks"):
        start = i
        p = Process(target=process_chunk, args=(in1, in2, out, start, chunk_size))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    in1.close()
    in2.close()
    out.close()

def main():
    args = parse_args_deal_baseband()

    start_time = time.time()

    chunk_size = 1024 * 1024  # Adjust as needed
    num_processes = args.t  # Assuming 't' is the argument for number of processes
    combine_baseband(args.file1, args.file2, args.o, chunk_size, num_processes)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total time taken: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
