"""
You need to read or write binary data, such as that found in images,
sound files, and so on.
"""

from pathlib import Path


def main():
    with (Path(__file__).parent / "data.bin").open("wb") as f:
        f.write(b"hello world")

    with (Path(__file__).parent / "data.bin").open("rb") as f:
        print(f.read())


if __name__ == "__main__":
    main()
