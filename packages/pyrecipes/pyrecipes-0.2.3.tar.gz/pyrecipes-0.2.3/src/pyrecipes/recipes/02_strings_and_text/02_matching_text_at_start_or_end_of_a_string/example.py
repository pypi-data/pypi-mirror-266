"""
You need to check the start or end of a string for specific text pattern
such as file extensions, url schemes etc.
"""

from urllib.request import urlopen

filename = "spam.txt"
url = "http://www.python.org"


def example_1():
    print(f'Checking if filename {filename} ends with the string ".txt"')
    print(filename.endswith(".txt"), end="\n\n")
    print(f'Checking if filename {filename} starts with "file:"')
    print(filename.startswith("file:"), end="\n\n")


def example_2():
    print(f"Checking if {url} starts wih either (http:|https|s3:|ftp:)")
    print(url.startswith(("http:", "https:", "s3:", "ftp:")))


def read_data(name):  # pragma: no cover
    if name.startswith(("http:", "https:", "ftp:")):
        return urlopen(name).read()
    else:
        with open(name, "r") as f:
            return f.read()


def main():
    example_1()
    example_2()


if __name__ == "__main__":
    main()
