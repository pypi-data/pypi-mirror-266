"""
You need to perform the same operation on many objects, bu the objects are
contained in different containers, and you'd like to avoid nested loops
without losing the readability of your code.
"""
from itertools import chain


def main():
    a = [1, 2, 3, 4]
    b = ["x", "y", "z"]

    print("a:", a, " | b:", b)
    for x in chain(a, b):
        print(x)

    # Various working sets of items
    active_items = set([1, 2, 3])
    inactive_items = set([4, 5, 6])

    for item in chain(active_items, inactive_items):
        # process item
        print(f"processing... {item}")


if __name__ == "__main__":
    main()
