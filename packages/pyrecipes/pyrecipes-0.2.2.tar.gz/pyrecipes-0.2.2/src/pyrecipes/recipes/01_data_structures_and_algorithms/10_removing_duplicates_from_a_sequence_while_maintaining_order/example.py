"""
You want to eliminate the duplicate values in a sequence,
but preserve the order of the remaining items
"""


def dedupe_hashable(items):
    seen = set()
    for item in items:
        if item not in seen:
            yield item
            seen.add(item)


def dedupe_unhashable(items, key):
    seen = set()
    for item in items:
        val = item if key is None else key(item)
        if val not in seen:
            yield item
            seen.add(val)


def main():
    a = [1, 5, 2, 1, 9, 1, 5, 10]
    b = [{"x": 1, "y": 2}, {"x": 1, "y": 3}, {"x": 1, "y": 2}, {"x": 2, "y": 4}]

    print(f"\nDe-duping {a} (hashable)")
    print(list(dedupe_hashable(a)))
    print("=" * 50)

    print(f"\nDe-duping {b} (unhashable)")
    print(" (de-duping on the x and y key values)")
    print(list(dedupe_unhashable(b, key=lambda d: (d["x"], d["y"]))))
    print("=" * 50)

    print(f"\nDe-duping {b} (unhashable)")
    print(" (de-duping on the x key value)")
    print(list(dedupe_unhashable(b, key=lambda d: d["x"])), end="\n\n")


if __name__ == "__main__":
    main()
