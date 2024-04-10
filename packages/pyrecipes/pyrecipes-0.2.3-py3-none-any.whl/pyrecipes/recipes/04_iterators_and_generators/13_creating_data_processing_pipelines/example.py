"""
You want to process data iteritively in the style of a data processing
pipeline (similar to Unix pipes). For instance, you have a huge amount
of data that needs to be processed but it can't entirely fit into memory.
"""

import os
import fnmatch
import gzip
import bz2
import re
from pathlib import Path


def gen_find(filepat, top):
    """
    Find all filenames in a directory tree that match a shell wildcard pattern.
    """
    for path, _, filelist in os.walk(top):
        for name in fnmatch.filter(filelist, filepat):
            yield os.path.join(path, name)


def gen_opener(filenames):
    """
    Open a sequence of filenames one at a time producing a file object.
    The file is closed immediately when proceeding to the next iteration.
    """
    for filename in filenames:
        if filename.endswith(".gz"):
            f = gzip.open(filename, "rt")
        elif filename.endswith(".bz2"):
            f = bz2.open(filename, "rt")
        else:
            f = open(filename, "rt")
        yield f
        f.close()


def gen_concatenate(iterators):
    """
    Chain a sequence of iterators together to a single sequence.
    """
    for iterator in iterators:
        yield from iterator


def gen_grep(pattern, lines):
    """
    Look for a regex pattern in a sequence of lines
    """
    pat = re.compile(pattern)
    for line in lines:
        if pat.search(line):
            yield line


def example_1():
    lognames = gen_find("access-log*", Path(__file__).parent / "data/")
    files = gen_opener(lognames)
    lines = gen_concatenate(files)
    pylines = gen_grep("(?i)python", lines)
    bytecolumns = (line.rsplit(None, 1)[1] for line in pylines)
    bytes_ = (int(x) for x in bytecolumns if x != "-")
    print(f"Bytes: {sum(bytes_):,}")


def example_2():
    total = 0
    lognames = gen_find("access-log*", Path(__file__).parent / "data/")
    files = gen_opener(lognames)
    lines = gen_concatenate(files)
    pylines = gen_grep("(?i)python", lines)
    total = (1 for _ in pylines)
    print(f"Lines: {sum(total):,}")


def main():
    example_1()
    example_2()


if __name__ == "__main__":
    main()
