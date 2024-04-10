"""
You want to read or write data encoded as a binary array of uniform
structures into Python tuples.
"""
from struct import Struct
from pathlib import Path


def write_records(records, fmt, f):
    """Write a sequence of tuples to a binary file or structure"""
    record_struct = Struct(fmt)
    for r in records:
        f.write(record_struct.pack(*r))


def read_records(fmt, f):
    record_struct = Struct(fmt)
    chunks = iter(lambda: f.read(record_struct.size), b"")
    return (record_struct.unpack(chunk) for chunk in chunks)


def example_1():
    records = [(1, 2.3, 4.5), (6, 7.8, 9.0), (12, 13.4, 56.7)]
    print("records:", records)

    with open(Path(__file__).parent / "data.b", "wb") as f:
        write_records(records, "<idd", f)


def example_2():
    with open(Path(__file__).parent / "data.b", "rb") as f:
        for rec in read_records("<idd", f):
            print(rec)


def main():
    example_1()
    example_2()


if __name__ == "__main__":
    main()
