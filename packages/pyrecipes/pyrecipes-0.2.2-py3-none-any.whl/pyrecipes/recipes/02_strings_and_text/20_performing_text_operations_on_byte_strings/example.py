"""
You want to perform common text operations (e.g. stripping, searching
and replacement) on byte strings.
"""

import re


def main():
    data = b"Hello World!"
    print("data:", data)
    print(data[:5])
    print(data.startswith(b"Hello"))
    print(data.split())
    print(data.replace(b"Hello", b"Hello Cruel"))
    print()

    data = bytearray(data)
    print("data:", data)
    print(data[:5])
    print(data.startswith(b"Hello"))
    print(data.split())
    print(data.replace(b"Hello", b"Hello Cruel"))
    print()

    data = b"FOO:BAR,SPAM"
    pattern = re.compile(b"[:,]")
    splits = re.split(pattern, data)
    print("data:", data)
    print("pattern:", pattern)
    print("splits:", splits)


if __name__ == "__main__":
    main()
