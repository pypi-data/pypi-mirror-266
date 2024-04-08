"""
Instead of iterating over a file by lines, you want to iterate
over a collection of fixed-sized records or chunks.
"""
from pathlib import Path
from functools import partial

RECORD_SIZE = 32


def main():
    with (Path(__file__).parent / "somefile.data").open("rb") as f:
        records = iter(partial(f.read, RECORD_SIZE), b"")
        for record in records:
            print(record)


if __name__ == "__main__":
    main()
