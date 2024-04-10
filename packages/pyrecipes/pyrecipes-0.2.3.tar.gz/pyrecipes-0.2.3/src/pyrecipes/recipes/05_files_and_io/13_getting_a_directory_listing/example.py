"""
You want to get a list of files contained in a directory on the filesystem.
"""
from pathlib import Path

somedir = Path(__file__).parent


def main():
    names = list(somedir.iterdir())
    print(names)

    # Get files
    print("\nfiles:")
    for name in names:
        if name.is_file():
            print(name)

    # Get dirs
    print("\ndirs:")
    for name in names:
        if name.is_dir():
            print(name)

    # Get specific files
    print("\n.py files")
    for name in names:
        if name.suffix == ".py":
            print(name)

    # Glob matching recursive
    print("\nglob matching pattern *.py")
    for name in somedir.glob("**/*.py"):
        print(name)


if __name__ == "__main__":
    main()
