"""
You want to read binary data directly into a mutable buffer without
any immediate copying. Perhaps you want to mutate the data in-place
and write it back out to a file.
"""
import os.path
from pathlib import Path


def read_into_buffer(filename):
    buf = bytearray(os.path.getsize(filename))
    with open(filename, "rb") as f:
        f.readinto(buf)
    return buf


def main():
    # Write sample file
    filename = Path(__file__).parent / "sample.bin"

    with filename.open("wb") as f:
        f.write(b"Hello World!")

    buf = read_into_buffer(filename)
    print(buf)
    print(buf[:5])
    buf[0:5] = b"hallo"
    print(buf)

    m1 = memoryview(buf)
    m2 = m1[-6:]
    print(m1, m2)
    m2[:] = b"WORLD!"
    print(buf)


if __name__ == "__main__":
    main()
