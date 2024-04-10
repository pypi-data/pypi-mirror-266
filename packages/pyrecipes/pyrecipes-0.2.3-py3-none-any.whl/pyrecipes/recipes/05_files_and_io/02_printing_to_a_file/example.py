"""
You want to redirect the output of the print() function to a file.
"""
from pathlib import Path


def main():
    with (Path(__file__).parent / "somefile.txt").open("wt") as f:
        print("hello world", file=f)


if __name__ == "__main__":
    main()
