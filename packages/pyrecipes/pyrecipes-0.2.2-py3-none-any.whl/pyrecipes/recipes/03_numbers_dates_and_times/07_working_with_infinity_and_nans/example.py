"""
You need to create or test for the floating-point values of infinity,
negative infinity or NaN (not a number).
"""
import math


def main():
    a = float("inf")
    b = float("-inf")
    c = float("nan")

    print("a:", a, "b:", b, "c:", c)
    print(math.isinf(a))
    print(math.isinf(b))
    print(math.isnan(a))
    print(math.isnan(c))

    print(10 * a)
    print(100 / c)

    # Subtlety - NaNs never compare as equal
    d, e = float("nan"), float("nan")
    print(d == e)


if __name__ == "__main__":
    main()
