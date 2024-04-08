"""
You want an instance to delegate attrbute access to an internally
held instance, possibly as an alternative to inheritance or in
order to implement a proxy.
"""


class A:
    def spam(self, x):
        print(f"{self}.spam:", x)

    def foo(self):
        print(f"{self}.foo called")

    def __repr__(self):
        return f"{self.__class__.__name__}"


class B:
    # If only a small number of methods to delegate
    def __init__(self):
        self._a = A()

    def spam(self, x):
        # Delegate to the internal self._a instance
        self._a.spam(x)

    def foo(self):
        # Delegate to the internal self._a instance
        self._a.foo()

    def bar(self):
        print(f"{self}.bar called")

    def __repr__(self):
        return f"{self.__class__.__name__}"


class C:
    # Alternative approach using __getattr__
    def __init__(self):
        self._a = A()

    def __getattr__(self, name):
        return getattr(self._a, name)

    def __repr__(self):
        return f"{self.__class__.__name__}"


def main():
    b = B()
    print(b)
    b.bar()
    b.foo()
    b.spam(1)

    c = C()
    print(c)
    c.foo()
    c.spam(1)


if __name__ == "__main__":
    main()
