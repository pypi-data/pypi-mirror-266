"""
You want to define a function or method where one or more of the
arguments are optional and have a default value.
"""


def spam(a, b=42):
    print(a, b)


def spam2(a, b=None):
    b = [] if b is None else b
    print(a, b)


def main():
    spam(1)
    spam(1, 2)
    spam2(1)
    spam2(2, [1, 2, 3])


if __name__ == "__main__":
    main()
