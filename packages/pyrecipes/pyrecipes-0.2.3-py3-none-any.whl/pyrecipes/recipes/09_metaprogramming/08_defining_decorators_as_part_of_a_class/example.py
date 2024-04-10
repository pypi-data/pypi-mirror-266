"""
You want to define a decorator inside a class deinition and apply it to
other functions or methods.
"""

from functools import wraps


class A:
    # Decorator as an instance method
    def decorator1(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print("Decorator 1")
            return func(*args, **kwargs)

        return wrapper

    # Decorator as a class method
    @classmethod
    def decorator2(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print("Decorator 2")
            return func(*args, **kwargs)

        return wrapper


def main():

    # As an instance method
    a = A()

    @a.decorator1
    def spam():
        print("Spam!")

    # As a class method
    @A.decorator2
    def grok():
        print("Grok!")

    spam()
    grok()


if __name__ == "__main__":
    main()
