"""
You want to iterate over the items contained in more than one sequence
at a time.
"""
from itertools import zip_longest


def main():
    xpts = [1, 5, 4, 2, 10, 7]
    ypts = [101, 78, 37, 15, 62, 99]

    print("xpts:", xpts, "| ypts:", ypts)
    for x, y in zip(xpts, ypts):
        print("(x, y):", (x, y))

    a = [1, 2, 3]
    b = ["w", "x", "y", "z"]

    print("\na:", a, " | b:", b)
    print("\ndefault zipping behaviour")
    for i in zip(a, b):
        print("(a, b):", i)

    print("\nusing zip_longest")
    for i in zip_longest(a, b):
        print("(a, b):", i)


if __name__ == "__main__":
    main()
