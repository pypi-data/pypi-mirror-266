"""
You want to iterate over all the possible combinations or permutations of a collection of items.
"""
from itertools import permutations, combinations


def main():
    items = ["a", "b", "c"]
    print(f"all permutations of {items}")
    for p in permutations(items):
        print(p)

    print(f"\nall permutations of {items} of length 2")
    for p in permutations(items, 2):
        print(p)

    print(f"all combinations of {items} of length 3")
    for c in combinations(items, 3):
        print(c)

    print(f"\nall combinations of {items} of length 2")
    for c in combinations(items, 2):
        print(c)

    print(f"\nall combinations of {items} of length 1")
    for c in combinations(items, 1):
        print(c)


if __name__ == "__main__":
    main()
