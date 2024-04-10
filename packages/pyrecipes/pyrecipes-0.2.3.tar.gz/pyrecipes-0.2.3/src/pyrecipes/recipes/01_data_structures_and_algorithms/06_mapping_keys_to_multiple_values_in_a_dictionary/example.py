"""
You want to make a dictionary that maps keys to more than one value
(a so-called 'multidict')
"""
from collections import defaultdict


def main():
    d = {"a": [1, 2, 3], "b": [4, 5]}
    print(d)

    e = {"a": {1, 2, 3}, "b": {4, 5}}
    print(e)

    d = defaultdict(list)
    d["a"].append(1)
    d["a"].append(2)
    d["b"].append(3)
    print(d)

    d = defaultdict(set)
    d["a"].add(1)
    d["a"].add(2)
    d["a"].add(2)
    d["b"].add(3)
    print(d)

    d = {}
    d.setdefault("a", []).append(1)
    d.setdefault("a", []).append(2)
    d.setdefault("a", []).append(3)
    print(d)


if __name__ == "__main__":
    main()
