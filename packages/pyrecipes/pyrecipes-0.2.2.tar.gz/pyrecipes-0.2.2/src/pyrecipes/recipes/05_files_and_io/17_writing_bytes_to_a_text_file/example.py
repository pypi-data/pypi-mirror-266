"""
You want to write raw bytes to a file opened in text mode.
"""
import sys


def main():
    try:
        sys.stdout.write(b"Hello\n")
    except TypeError as exc:
        print("Caught exception:", exc)

    sys.stdout.buffer.write(b"Hello\n")


if __name__ == "__main__":
    main()
