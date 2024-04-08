"""
You want to strip unwanted characters, such as whitespace, from the
beginning, end or middle of a text string.
"""


def main():
    s = "     hello world     \n"
    print("s:", s)
    print("s.strip(): ", s.strip())
    print("s.lstrip():", s.lstrip())
    print("s.rstrip():", s.rstrip())
    print()

    t = "-----hello====="
    print("t:", t)
    print("t.lstrip('-'):", t.lstrip("-"))
    print("t.rstrip('='):", t.rstrip("="))
    print("t.strip('-='):", t.strip("-="))


if __name__ == "__main__":
    main()
