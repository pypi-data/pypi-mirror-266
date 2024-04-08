"""
You want to wrap functions with a decorator, but the result is going
to be a callable instance. You need your decorator to work both inside
and outside class definitions.
"""

import types
from functools import wraps


class Profiled:
    def __init__(self, func):
        wraps(func)(self)
        self.ncalls = 0

    def __call__(self, *args, **kwargs):
        self.ncalls += 1
        return self.__wrapped__(*args, **kwargs)

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return types.MethodType(self, instance)


@Profiled
def add(x, y):
    return x + y


class Spam:
    @Profiled
    def bar(self, x):
        print(self, x)


def main():
    print("add 1 + 2:", add(1, 2))
    print("add 3 + 4:", add(3, 4))
    print("add ncalls:", add.ncalls)

    s = Spam()
    s.bar(2)
    s.bar(3)
    s.bar(4)
    print("Spam bar ncalls:", Spam.bar.ncalls)


if __name__ == "__main__":
    main()
