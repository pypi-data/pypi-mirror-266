"""
You want to memory map a binary file into a mutable byte array, possibly
for random access to it's contents of in-place modifications.
"""
import os
import mmap
from pathlib import Path


def memory_map(filename, access=mmap.ACCESS_WRITE):
    size = os.path.getsize(filename)
    fd = os.open(filename, os.O_RDWR)
    return mmap.mmap(fd, size, access=access)


def main():
    size = 100000
    filename = Path(__file__).parent / "somefile.data"
    with filename.open("wb") as f:
        f.seek(size - 1)
        f.write(b"\x00")

    with memory_map(filename) as m:
        print(m)
        print(len(m))
        print(m[:10])
        m[0:11] = b"Hello World"
        print("memorymap closed:", m.closed)
    print("memorymap closed:", m.closed)

    with filename.open("rb") as f:
        print(f.read(15))


if __name__ == "__main__":
    main()
