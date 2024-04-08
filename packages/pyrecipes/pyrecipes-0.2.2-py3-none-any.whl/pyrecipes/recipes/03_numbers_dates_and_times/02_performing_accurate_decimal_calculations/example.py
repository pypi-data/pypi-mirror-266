"""
You need to perform accurate calculations with decimal numbers, and don't
the small errors that naturally occur with floats.
"""

from decimal import Decimal


def example_floats():
    print("floats...")
    a = 4.2
    b = 2.1
    print("a:", a)
    print("b:", b)
    print("a + b:", a + b)
    print("a + b == 6.3:", (a + b) == 6.3)
    print()


def example_decimals():
    print("decimals...")
    a = Decimal("4.2")
    b = Decimal("2.1")
    print("a:", a)
    print("b:", b)
    print("a + b:", a + b)
    print("a + b == 6.3:", (a + b) == Decimal("6.3"))
    print()


def main():
    example_floats()
    example_decimals()


if __name__ == "__main__":
    main()
