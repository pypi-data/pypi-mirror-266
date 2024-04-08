"""
You have entered a time machine and suddenly find yourself working
on elemntary-level homework problems involving fractions. Or perhaps
you're writing code to make calculations involving measurements
made in your wood shop.
"""
from fractions import Fraction


def main():
    a = Fraction(5, 4)
    b = Fraction(7, 16)
    print("a:", a, "b:", b)
    print("a + b:", a + b)
    print("a - b:", a - b)
    print("a * b:", a * b)
    print("a / b:", a / b)

    c = a * b
    print(c)
    print(c.numerator)
    print(c.denominator)
    print(float(c))
    print(c.limit_denominator(8))

    x = 3.75
    y = Fraction(*x.as_integer_ratio())
    print(x, y)


if __name__ == "__main__":
    main()
