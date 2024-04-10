"""
You need to perform calculations on large numerical datasets,
such as arrays or grids.
"""
import numpy as np


def main():
    # Lists
    x = [1, 2, 3, 4]
    y = [5, 6, 7, 8]
    print("x:", x, "y:", y)
    print("x * 2:", x * 2)
    print("x + y:", x + y)
    try:
        print("x + 10:", x + 10)
    except Exception as exc:
        print("x + 10:", exc)
    print()

    # NumPy arrays
    ax = np.array(x)
    ay = np.array(y)
    print("ax:", ax, "ay:", ay)
    print("ax * 2:", ax * 2)
    print("ax + ay:", ax + ay)
    print("ax + 10:", ax + 10)
    print("ax * ay:", ax * ay)
    print(np.sqrt(ax))
    print(np.cos(ax))
    print()

    # Grids
    m = np.zeros(shape=(1000, 1000), dtype=float)
    print(m)
    m += 10
    print(m)
    print(np.sin(m))

    # Slicing and changing subsections
    a = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])
    print(a)
    print(a[1])
    print(a[:, 1])
    print(a[1:3, 1:3])
    a[1:3, 1:3] += 10
    print(a)

    # Broadcast row vector across an operation on all rows
    print(a + [100, 101, 102, 103])

    # Conditional assignment
    print(np.where(a < 10, a, 10))


if __name__ == "__main__":
    main()
