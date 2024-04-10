"""
You need to create a temporary file or directory for use when your program
executes. Afterwards, you possible want the file or directory to be destroyed.
"""
from tempfile import TemporaryDirectory, TemporaryFile, NamedTemporaryFile
from pathlib import Path


def example_1():
    """Unnamed temp file"""
    with TemporaryFile("w+t") as f:
        # Read / Write to the file
        f.write("Hello World!\n")
        f.write("Testing\n")

        # Seek back to beginning and read
        f.seek(0)
        data = f.read()
        print(data)
    # Temp file is destoyed
    print()


def example_2():
    """Named temp file"""
    with NamedTemporaryFile("w+t") as f:
        temp_file_name = f.name
        print("tmp file:", temp_file_name)
        print("exists:", Path(temp_file_name).exists())
    print("Temp file destroyed")
    print("exists:", Path(temp_file_name).exists())
    print()


def example_3():
    """Temp directory"""
    with TemporaryDirectory() as dirname:
        print("tmp dirname:", dirname)
        print("exists:", Path(dirname).exists())
    print("tmp dir destroyed")
    print("exists:", Path(dirname).exists())
    print()


def main():
    example_1()
    example_2()
    example_3()


if __name__ == "__main__":
    main()
