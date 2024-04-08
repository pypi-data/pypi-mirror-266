"""
You are writing a lot of classes that serve as data structures, but are
getting tired of writing highly repetitive and boilerplate __init__()
functions.
"""

import math


class Structure:
    # class variable that specifies expected fields
    _fields = []

    def __init__(self, *args, **kwargs):
        n = len(self._fields)
        if len(args) != n:
            raise TypeError(f"Expected {n} fields")

        # Set required arguments
        for name, value in zip(self._fields, args):
            setattr(self, name, value)

        # Set additional arguments if any
        extra_args = kwargs.keys() - self._fields
        for name in extra_args:
            setattr(self, name, kwargs.pop(name))
        if kwargs:
            raise TypeError(f'Duplicated values for {",".join(kwargs)}')


class Stock(Structure):
    _fields = ["name", "shares", "price"]


class Point(Structure):
    _fields = ["x", "y"]


class Circle(Structure):
    _fields = ["radius"]

    @property
    def area(self):
        return math.pi * self.radius**2


def main():
    s1 = Stock("AAPL", 10, 100)
    s2 = Stock("MSFT", 10, 95, date="2023-01-01")
    c = Circle(4.0)
    print(s1.name)
    print(s1.price)
    print(s2.date)
    print(c.radius)
    print(c.area)


if __name__ == "__main__":
    main()
