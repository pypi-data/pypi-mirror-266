"""
You need to read or write data in a file with gzip of bz2 compression.
"""
import gzip
import bz2
from pathlib import Path


THIS_DIR = Path(__file__).parent


def main():
    # Writing
    with gzip.open(THIS_DIR / "somefile.gz", "wt") as f:
        f.write("Hello World!")

    with bz2.open(THIS_DIR / "somfile.bz2", "wt") as f:
        f.write("Hello World!")

    # Reading
    with gzip.open(THIS_DIR / "somefile.gz", "rt") as f:
        text = f.read()
        print(text)

    with bz2.open(THIS_DIR / "somfile.bz2", "rt") as f:
        text = f.read()
        print(text)


if __name__ == "__main__":
    main()
