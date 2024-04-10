"""
You have code that uses a while loop to iteratively process data because it
involves a function or some kind of unusual test condition that doesn't fall
into the usual iteration pattern.
"""
import sys
from pathlib import Path

CHUNKSIZE = 1024


def main():
    """
    ######################################################
    # Common pattern
    def process_data(data):
        pass


    def reader_orig(s):
        while True:
            data = s.recv(CHUNKSIZE)
            if data == b'':
                break
            process_data(data)


    ######################################################
    # Better approach - iter takes optional sentinel param
    def reader(s):
        for chunk in iter(lambda: s.recv(CHUNKSIZE, b'')):
            process_data(chunk)
    """
    with open(Path(__file__).parent / "access-log", "r") as f:
        for chunk in iter(lambda: f.read(10), ""):
            sys.stdout.write(chunk)


if __name__ == "__main__":
    main()
