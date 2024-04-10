"""
You need to manipulate pathnames in order to find the base filename,
directory name, absolute path, and so on.
"""
from pathlib import Path


def main():
    path = Path("/Users/cadams/Data/data.csv")
    print(path)
    print(path.name)
    print(path.parent)
    print(Path("tmp").joinpath("data", path.name))

    path = Path("~/Data/data.csv")
    print(path)
    print(path.expanduser())
    print(path.suffix)


if __name__ == "__main__":
    main()
