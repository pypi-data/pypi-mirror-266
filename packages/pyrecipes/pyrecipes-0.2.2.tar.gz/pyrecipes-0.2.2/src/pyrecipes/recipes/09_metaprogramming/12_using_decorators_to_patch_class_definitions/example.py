"""
You want to inspect or rewrite portions of a class definition
to alter its behavior, but without using inheritance or metaclasses.
"""


def log_getattribute(cls):
    # Get the original implementation
    orig_getattribute = cls.__getattribute__

    # Make a new definition
    def new_getattribute(self, name):
        print("getting:", name)
        return orig_getattribute(self, name)

    # Attach to the class and return
    cls.__getattribute__ = new_getattribute
    return cls


# Example use
@log_getattribute
class A:
    def __init__(self, x):
        self.x = x

    def spam(self):
        pass


def main():
    a = A(42)
    print(a.x)
    a.spam()


if __name__ == "__main__":
    main()
