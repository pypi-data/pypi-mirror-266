"""
You have a callable that you would like to use with some other Python
code, possibly as a callback function of handler, but it takes too
many arguments and causes an exception when called.
"""
import math
from functools import partial


def spam(a, b, c, d):
    print(a, b, c, d)


def distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.hypot(x2 - x1, y2 - y1)


def example_1():
    s1 = partial(spam, 1)
    s1(2, 3, 4)
    s1(4, 5, 6)

    s2 = partial(spam, d=42)
    s2(1, 2, 3)
    s2(4, 5, 5)

    s3 = partial(spam, 1, 2, d=42)
    s3(3)
    s3(4)
    s3(5)


def example_2():
    points = [
        (1, 2),
        (3, 4),
        (5, 6),
        (7, 8),
    ]
    print("points", points)
    pt = (4, 3)
    print("pt:", pt)
    points.sort(key=partial(distance, pt))
    print("sorted:", points)


def main():
    example_1()
    example_2()


if __name__ == "__main__":
    main()
