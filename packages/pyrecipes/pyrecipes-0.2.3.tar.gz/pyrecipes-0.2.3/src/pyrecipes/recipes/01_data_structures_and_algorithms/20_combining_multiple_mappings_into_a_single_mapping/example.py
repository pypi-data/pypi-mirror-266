"""
You have multiple dictionaries or mappings that you want to logically
combine into a single mapping to perform certain operations, such as
looking up values or checking for the existence of keys.
"""

from collections import ChainMap


def main():
    a = {"x": 1, "z": 3}
    b = {"y": 2, "z": 4}

    print("dict a:", a)
    print("dict b:", a)

    c = ChainMap(a, b)
    print("ChainMap c:", c)
    for x in list("xyz"):
        print(f"ChainMap[{x}]:", c[x])
    print("ChainMap keys:", list(c.keys()))
    print("ChainMap values:", list(c.values()))
    print("ChainMap items:", list(c.items()))


if __name__ == "__main__":
    main()
