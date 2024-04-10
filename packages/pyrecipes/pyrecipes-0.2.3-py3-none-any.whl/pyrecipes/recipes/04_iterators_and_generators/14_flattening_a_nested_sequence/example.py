"""
You have a nested sequence that you want to flatten into a single list of values.
"""
from collections.abc import Iterable


def flatten(items, ignore_types=(str, bytes)):
    for item in items:
        if isinstance(item, Iterable) and not isinstance(item, ignore_types):
            yield from flatten(item, ignore_types)
        else:
            yield item


def main():
    items = [1, 2, [3, 4, [5, 6], 7], 8]
    print(f"Items: {items}")
    print(f"flattened: {list(flatten(items))}")

    print("\niterating over items")
    for x in items:
        print(x)

    print("\niterating over flattened items")
    for x in flatten(items):
        print(x)


if __name__ == "__main__":
    main()
