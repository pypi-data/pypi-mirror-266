"""
You need to process items in an iterator, but for whatever reason
you can't or don't want to use a for loop.
"""

from pathlib import Path


def main():
    with open(Path(__file__).parent / "somefile.txt", "r") as f:
        try:
            while True:
                line = next(f)
                print(line.rstrip("\n"), end="")
        except StopIteration:
            pass


if __name__ == "__main__":
    main()
