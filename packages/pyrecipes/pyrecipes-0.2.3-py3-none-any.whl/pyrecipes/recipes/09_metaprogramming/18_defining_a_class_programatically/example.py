"""
You're writing code that ultimately needs to create a new class object. You've
thought about emitting class source code to a string and using a function
such as exec() to evaluate it, but you'd prefer a more elegant solution.
"""

import sys
import types
import operator


def example_1():
    # Example of making a class manually from parts
    # Methods
    def __init__(self, name, shares, price):
        self.name = name
        self.shares = shares
        self.price = price

    def cost(self):
        return self.shares * self.price

    cls_dict = {
        "__init__": __init__,
        "cost": cost,
    }

    # Make a class
    Stock = types.new_class("Stock", (), {}, lambda ns: ns.update(cls_dict))

    s = Stock("ACME", 50, 91.1)
    print(s)
    print(s.cost())


def example_2():
    # An alternative formulation of namedtuples
    def named_tuple(classname, fieldnames):
        # Populate a dictionary of field property accessors
        cls_dict = {
            name: property(operator.itemgetter(n)) for n, name in enumerate(fieldnames)
        }

        # Make a __new__ function and add to the class dict
        def __new__(cls, *args):
            if len(args) != len(fieldnames):
                raise TypeError("Expected {} arguments".format(len(fieldnames)))
            return tuple.__new__(cls, (args))

        cls_dict["__new__"] = __new__

        # Make the class
        cls = types.new_class(classname, (tuple,), {}, lambda ns: ns.update(cls_dict))
        cls.__module__ = sys._getframe(1).f_globals["__name__"]
        return cls

    Point = named_tuple("Point", ["x", "y"])
    print(Point)
    p = Point(4, 5)
    print(len(p))
    print(p.x, p[0])
    print(p.y, p[1])
    try:
        p.x = 2
    except AttributeError as e:
        print(e)
    print("%s %s" % p)


def main():
    example_1()
    example_2()


if __name__ == "__main__":
    main()
