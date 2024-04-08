"""
You would like to extend a closure with functions that allow the inner
variable to be accessed and modified.
"""
import sys


def sample():
    n = 0

    # Closure function
    def func():
        print("n =", n)

    # Accessor methods for n
    def get_n():
        return n

    def set_n(value):
        nonlocal n
        n = value

    # Attach as function attributes
    func.get_n = get_n
    func.set_n = set_n
    return func


class ClosureInstance:
    def __init__(self, locals=None):
        if locals is None:
            locals = sys._getframe(1).f_locals

        # Update the instance dict with callables
        self.__dict__.update(
            (key, value) for key, value in locals.items() if callable(value)
        )

    # Redirect special methods
    def __len__(self):
        return self.__dict__["__len__"]()


def Stack():
    items = []

    def push(item):
        items.append(item)

    def pop():
        return items.pop()

    def __len__():
        return len(items)

    return ClosureInstance()


def example_1():
    f = sample()
    f()
    f.set_n(10)
    f()
    print(f.get_n())


def example_2():
    s = Stack()
    print(s)
    s.push(10)
    s.push(20)
    s.push("Hello")
    n = len(s)
    print(n)
    for i in range(n):
        val = s.pop()
        print(val)


def main():
    example_1()
    example_2()


if __name__ == "__main__":
    main()
