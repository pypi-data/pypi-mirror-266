"""
You need to split a string into fields, but the delimiters (and spacing around them) aren't consitent
thoughout the string.
"""

import re

line = "asdf fjdk; afed, fjek,asdf       foo"


def example_1():
    pat = r"[;,\s]\s*"
    print("Example 1")
    print(f"Splitting the line:\n\t{line}")
    print(f'using the regex pattern "{pat}"\n')
    print(f"Fields: {re.split(pat, line)}")
    print("=" * 50)


def example_2():
    pat = r"([;,\s])\s*"
    print("Example 2")
    print(f"Splitting the line:\n\t{line}")
    print(f'using the regex pattern "{pat}"')
    print("notice this time how the regex pattern contains a capture group\n")
    fields = re.split(pat, line)
    values = fields[::2]
    delimiters = fields[1::2] + [""]
    print(f"Fields: {fields}")
    print(f"Values: {values}")
    print(f"Delimiters: {delimiters}")
    print(
        f'Reconstructed example: {"".join(v + d for v, d in zip(values, delimiters))}'
    )
    print("=" * 50)


def main():
    example_1()
    example_2()


if __name__ == "__main__":
    main()
