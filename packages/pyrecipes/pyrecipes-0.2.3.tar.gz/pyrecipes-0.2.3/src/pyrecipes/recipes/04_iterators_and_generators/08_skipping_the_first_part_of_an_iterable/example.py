"""
You want to iterate over an iterable, but the first few items aren't of interest
and you just want to discard them.
"""

from itertools import dropwhile
from pathlib import Path


def main():
    with open(Path(__file__).parent / "somefile.txt", "r") as f:
        for line in dropwhile(lambda line: line.startswith("#"), f):
            print(line, end="")


if __name__ == "__main__":
    main()
