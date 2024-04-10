"""
You want to match text using the same wildcard patterns as are commonly
used when working in Unix shells (e.g. *.py, Dat[0-9]*.csv etc)
"""

from fnmatch import fnmatch, fnmatchcase


def match(term, pattern, case=False):
    result = fnmatchcase(term, pattern) if case else fnmatch(term, pattern)
    result = f'"{term}" matches "{pattern}": {result}'
    if case:
        result += " (case-sensitive)"
    return result


def main():
    print(match("foo.txt", "*.txt"))
    print(match("foo.txt", "?oo.txt"))
    print(match("Dat45.csv", "Dat[0-9]*.csv"))
    print(match("foo.txt", "*.TXT", case=True))


if __name__ == "__main__":
    main()
