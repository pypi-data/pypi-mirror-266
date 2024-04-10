"""
You want to write data to a file, but only if it doesn't already exist
on a filesystem.
"""

from pathlib import Path


def main():
    with (Path(__file__).parent / "somefile.txt").open("w+") as f:
        f.write("hello world")

    try:
        with (Path(__file__).parent / "somefile.txt").open("xt") as f:
            print(f.read())
    except FileExistsError:
        print("file already exists!")


if __name__ == "__main__":
    main()
