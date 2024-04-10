"""
You want to add of change the Unicode encoding of an already open file
without closing it first.
"""
import io
import sys
import urllib.request


def example_1():
    """For illustrative purposes only"""
    u = urllib.request.urlopen("http://www.python.org")
    f = io.TextIOWrapper(u, encoding="utf-8")
    text = f.read()
    print(text)


def example_2():
    """For illustrative purposes only"""
    print(sys.stdout.encoding)
    sys.stdout = io.TextIOWrapper(sys.stdout.detatch(), encoding="latin-1")
    print(sys.stdout.encoding)


def main():
    pass


if __name__ == "__main__":
    main()
