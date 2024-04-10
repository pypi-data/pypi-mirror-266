"""
You are using regular expressions to process text, but are
concerned about the handling of Unicode characters.
"""

import re


def main():
    num = re.compile(r"\d+")
    print("num:", num)
    print("match 123:", num.match("123"))
    print("match \u0661\u0662\u0663", num.match("123"))
    print()

    pat = re.compile("stra\u00dfe", re.IGNORECASE)
    s = "straße"

    print("pat:", pat)
    print("s:", s)
    print("s matches:", pat.match(s))
    print("s matches UPPER:", pat.match(s.upper()))
    print("s.upper():", s.upper())


if __name__ == "__main__":
    main()
