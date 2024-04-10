"""
You've written a function or method that uses *args and **kwargs, so
that it can be general purpose, but you would also like to check the
passed arguments to see if they match a specific function calling
signature.
"""

from inspect import Signature, Parameter

# Create a signature for a func(x, y=42, *, z=None)
params = [
    Parameter("x", Parameter.POSITIONAL_OR_KEYWORD),
    Parameter("y", Parameter.POSITIONAL_OR_KEYWORD, default=42),
    Parameter("z", Parameter.KEYWORD_ONLY, default=None),
]
sig = Signature(params)


def func(*args, **kwargs):
    bound_values = sig.bind(*args, **kwargs)
    for name, value in bound_values.arguments.items():
        print(name, value)
    print()


def make_sig(*names):
    parms = [Parameter(name, Parameter.POSITIONAL_OR_KEYWORD) for name in names]
    return Signature(parms)


class StructureMeta(type):
    def __new__(cls, clsname, bases, clsdict):
        clsdict["__signature__"] = make_sig(*clsdict.get("_fields", []))
        return super().__new__(cls, clsname, bases, clsdict)


class Structure(metaclass=StructureMeta):
    _fields = []

    def __init__(self, *args, **kwargs):
        bound_values = self.__signature__.bind(*args, **kwargs)
        for name, value in bound_values.arguments.items():
            setattr(self, name, value)


# Example
class Stock(Structure):
    _fields = ["name", "shares", "price"]


class Point(Structure):
    _fields = ["x", "y"]


def example_1():
    print("sig:", sig, end="\n\n")
    print("func(1, 2, z=3)")
    func(1, 2, z=3)

    print("func(1)")
    func(1)

    print("func(1, z=3)")
    func(1, z=3)

    print("func(y=2, x=1)")
    func(y=2, x=1)

    print("func(1, 2, 3, 4)")
    try:
        func(1, 2, 3, 4)
    except TypeError as exc:
        print(exc, end="\n\n")

    print("func(y=2)")
    try:
        func(y=2)
    except TypeError as exc:
        print(exc, end="\n\n")


def example_2():
    s1 = Stock("ACME", 100, 490.1)
    print(s1.name, s1.shares, s1.price)

    s2 = Stock(shares=100, name="ACME", price=490.1)
    print(s2.name, s2.shares, s2.price)

    # Not enough args
    try:
        _ = Stock("ACME", 100)
    except TypeError as e:
        print(e)

    # Too many args
    try:
        _ = Stock("ACME", 100, 490.1, "12/21/2012")
    except TypeError as e:
        print(e)

    # Replicated args
    try:
        _ = Stock("ACME", 100, name="ACME", price=490.1)
    except TypeError as e:
        print(e)


def main():
    example_1()
    example_2()


if __name__ == "__main__":
    main()
