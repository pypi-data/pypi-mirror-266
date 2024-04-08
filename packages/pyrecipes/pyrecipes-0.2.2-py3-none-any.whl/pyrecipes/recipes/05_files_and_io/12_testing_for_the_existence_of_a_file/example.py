"""
You need to test whether or not a file or directory exists.
"""
from pathlib import Path


def main():
    for path in ["/tmp", __file__, "/totally/fake/path"]:
        print(path)
        print("exists:", Path(path).exists())
        print("is file:", Path(path).is_file())
        print("is dir:", Path(path).is_dir())
        print("is symlink:", Path(path).is_symlink())
        print()


if __name__ == "__main__":
    main()
