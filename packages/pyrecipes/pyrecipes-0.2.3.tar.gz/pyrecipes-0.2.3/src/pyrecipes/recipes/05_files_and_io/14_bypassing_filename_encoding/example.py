"""
You want to perform I/O operations using raw filenames that have not
been decoded or encoded according to the default filename encoding.
"""
import sys
import os
from pathlib import Path

parent_dir = Path(__file__).parent
parent_dir_encoded = str(parent_dir).encode()


def main():
    print(sys.getfilesystemencoding())

    # Write a file using unicode filename
    with parent_dir.joinpath("jalape\xf1o.txt").open("w") as f:
        f.write("Spicy!")

    # Directory listing (decoded)
    txt_files = [file for file in os.listdir(parent_dir) if file.endswith(".txt")]
    print(txt_files)

    # Directory listing (raw)
    txt_files = [
        file for file in os.listdir(parent_dir_encoded) if file.endswith(b".txt")
    ]
    print(txt_files)

    # Opening file with raw name
    with open(os.path.join(parent_dir_encoded, txt_files[0]), "r") as f:
        print(f.read())


if __name__ == "__main__":
    main()
