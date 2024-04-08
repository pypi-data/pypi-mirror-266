"""
You want to add extra processing (e.g. type checking or validation) to
the getting or setting of an instance attribute.
"""

import math


class Person:
    def __init__(self, first_name):
        self.first_name = first_name

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        if not isinstance(value, str):
            raise TypeError("Expected a string.")
        self._first_name = value

    @first_name.deleter
    def first_name(self):
        raise AttributeError("Can't delete attribute.")


class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        return math.pi * self.radius**2

    @property
    def circumference(self):
        return math.pi * 2 * self.radius


def example_1():
    person = Person("Chris")
    print(person.first_name)

    try:
        person.first_name = 2
    except TypeError as exc:
        print(exc)

    person.first_name = "Bob"
    print(person.first_name)

    try:
        del person.first_name
    except AttributeError as exc:
        print(exc)


def example_2():
    c = Circle(4.0)
    print(c.radius)
    print(c.area)
    print(c.circumference)


def main():
    example_1()
    example_2()


if __name__ == "__main__":
    main()
