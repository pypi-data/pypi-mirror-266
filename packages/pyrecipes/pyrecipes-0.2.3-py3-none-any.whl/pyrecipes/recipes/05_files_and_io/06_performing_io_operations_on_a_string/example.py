"""
You want to feed a text or binary string to code that's been written
to operate on file-like objects instead.
"""

import io


def main():
    s = io.StringIO()
    s.write("Hello world\n")
    print("this is a test", file=s)
    print(s.getvalue())

    s.seek(0)
    print(s.read(4))
    print(s.read())


if __name__ == "__main__":
    main()
