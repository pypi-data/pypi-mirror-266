"""
You're trying to match a text pattern using regular expressions, but
it is identifying the longest possible match of a pattern. Instead,
you would like to change it to find the shortest possible match.
"""

import re


def main():
    str_pat = re.compile(r"\"(.*)\"")
    text1 = 'computer says "no."'
    matches = str_pat.findall(text1)
    print("pattern:", str_pat)
    print("text:", text1)
    print("matches:", matches)

    text2 = 'computer says "no." Phone says "yes."'
    matches = str_pat.findall(text2)
    print("text2:", text2)
    print("matches:", matches)
    print()

    str_pat = re.compile(r"\"(.*?)\"")
    matches = str_pat.findall(text2)
    print("pattern:", str_pat)
    print("text2:", text2)
    print("matches:", matches)


if __name__ == "__main__":
    main()
