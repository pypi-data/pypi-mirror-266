"""
You've defined an anonymous function using lambda, but you also need
to capture the values of certain variables at the time of definition.
"""


def example_1():
    print("example 1")
    x = 10
    a = lambda y: x + y
    x = 20
    b = lambda y: x + y

    print(a(10))
    print(b(10))

    x = 15
    print(a(10))
    print()


def example_2():
    print("example 2")
    x = 10
    a = lambda y, x=x: x + y
    x = 20
    b = lambda y, x=x: x + y
    print(a(10))
    print(b(10))
    print()


def example_3():
    print("example 3")
    funcs = [lambda x, n=n: x + n for n in range(5)]
    for f in funcs:
        print(f(0))
    print()


def main():
    example_1()
    example_2()
    example_3()


if __name__ == "__main__":
    main()
