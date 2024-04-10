"""
You want to implement a custom class that mimics the behaviour of a
common built-in container type such as a list or dictionary. However,
you are not entirely sure what methods need to be implemented to do it.
"""
import collections
import bisect


class A(collections.abc.Iterable):
    # Required dunder-method to inherit from Iterable
    def __iter__(self):
        pass

    def __repr__(self):
        return "A()"


class SortedItems(collections.abc.Sequence):
    def __init__(self, initial=None):
        self._items = sorted(initial) if initial is not None else []

    # Required for Sequence
    def __getitem__(self, index):
        return self._items[index]

    # Required for Sequence
    def __len__(self):
        return len(self._items)

    def add(self, item):
        bisect.insort(self._items, item)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._items})"


class Items(collections.abc.MutableSequence):
    pass


def main():
    a = A()
    print(a)

    sorted_items = SortedItems([3, 2, 5])
    print(sorted_items)
    print(len(sorted_items))
    sorted_items.add(1)
    print(sorted_items)
    print(len(sorted_items))

    try:
        Items()
    except TypeError as exc:
        print(exc)


if __name__ == "__main__":
    main()
