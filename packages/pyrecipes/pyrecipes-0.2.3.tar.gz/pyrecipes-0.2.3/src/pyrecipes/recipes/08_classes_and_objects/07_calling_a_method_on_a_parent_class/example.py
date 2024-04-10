"""
You want to invoke a method in a parent class in place of a method
that has been overridden in a subclass.
"""


class A:
    def spam(self):
        print("A.spam")


class B(A):
    def spam(self):
        print("B.spam")
        super().spam()


class C:
    def __init__(self):
        self.x = 0


class D(C):
    def __init__(self):
        super().__init__()
        self.y = 1


def example_1():
    a = A()
    b = B()
    a.spam()
    b.spam()


def example_2():
    c = C()
    d = D()
    print(c.x)
    print(d.x)
    print(d.y)


def main():
    example_1()
    example_2()


if __name__ == "__main__":
    main()
