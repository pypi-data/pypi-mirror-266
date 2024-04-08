"""
You want to return multiple values from a function.
"""


def my_func():
    return 1, 2, 3


def main():
    a, b, c = my_func()
    print(a, b, c)


if __name__ == "__main__":
    main()
