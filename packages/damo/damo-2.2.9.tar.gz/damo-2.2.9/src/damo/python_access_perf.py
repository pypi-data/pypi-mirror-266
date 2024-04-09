import sys
import time

import _damo_fmt_str

mem_size = int(sys.argv[1])
memory = bytearray(mem_size)

print_time = time.time() + 1
nr_accessed = 0
while True:
    sum_ = 0
    for addr in range(0, mem_size, 4096):
        sum_ += memory[addr]
    nr_accessed += 1
    if time.time() >= print_time:
        print('%s per sec' % _damo_fmt_str.format_sz(mem_size * nr_accessed, machine_friendly=False))
        nr_accessed = 0
        print_time = time.time() + 1
