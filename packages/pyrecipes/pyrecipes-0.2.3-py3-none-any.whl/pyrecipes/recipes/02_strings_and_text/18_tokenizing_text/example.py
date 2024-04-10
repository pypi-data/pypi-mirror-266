"""
You have a string of text that you want to parse left to right
into a stream of tokens.
"""
import re
from collections import namedtuple

NAME = r"(?P<NAME>[a-zA-Z_][a-zA-Z_0-9]*)"
NUM = r"(?P<NUM>\d+)"
PLUS = r"(?P<PLUS>\+)"
TIMES = r"(?P<TIMES>\*)"
EQ = r"(?P<EQ>=)"
WS = r"(?P<WS>\s+)"

Token = namedtuple("Token", ["type", "value"])


def generate_tokens(pat, text):
    scanner = pat.scanner(text)
    for m in iter(scanner.match, None):
        yield Token(m.lastgroup, m.group())


def main():
    text = "foo = 23 + 42 * 10"
    master_pat = re.compile("|".join([NAME, NUM, PLUS, TIMES, EQ, WS]))
    scanner = master_pat.scanner(text)

    print(text)
    print(master_pat)
    for i in range(3):
        m = scanner.match()
        print(m, m.lastgroup, m.group())

    for tok in generate_tokens(master_pat, text):
        print(tok)


if __name__ == "__main__":
    main()
