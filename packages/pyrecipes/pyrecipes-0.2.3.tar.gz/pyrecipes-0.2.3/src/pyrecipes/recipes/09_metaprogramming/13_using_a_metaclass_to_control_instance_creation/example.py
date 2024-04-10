"""
You want to change the way in which instances are created in order to
implement singletons, caching, or other similar features.
"""

import weakref


class NoInstances(type):
    def __call__(self, *args, **kwargs):
        raise TypeError("Can't instantiate directly.")


class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance


class Cached(type):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__cache = weakref.WeakValueDictionary()

    def __call__(self, *args):
        if args in self.__cache:
            return self.__cache[args]
        else:
            obj = super().__call__(*args)
            self.__cache[args] = obj
            return obj


def example_1():
    class Spam(metaclass=NoInstances):
        @staticmethod
        def grok(x):
            print("Spam.grok:", x)

    print("Example 1 - No instances")
    try:
        spam = Spam()
        spam.grok("foo")
    except TypeError as exc:
        print(exc)

    Spam.grok("foo")


def example_2():
    class Spam(metaclass=Singleton):
        def __init__(self):
            print("Creating spam")

    print("Example 2 - Implements Singleton")
    a = Spam()
    b = Spam()
    print("a is b:", a is b)
    c = Spam()
    print("c ia a:", c is a)


def example_3():

    class Spam(metaclass=Cached):
        def __init__(self, name):
            print(f"Creating Spam({name})")
            self.name = name

    print("Example 3 - Cached implementation")
    a = Spam("foo")
    b = Spam("bar")
    c = Spam("foo")  # cached

    print("a is b:", a is b)
    print("a is b:", a is c)


def main():
    example_1()
    example_2()
    example_3()


if __name__ == "__main__":
    main()
