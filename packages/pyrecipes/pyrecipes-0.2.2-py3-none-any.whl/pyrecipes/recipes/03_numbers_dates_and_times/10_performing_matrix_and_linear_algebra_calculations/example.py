"""
You need to perform matrix and linear algebra operations, such as
matrix multiplication, finding determinants, solving linear equations
and so on.
"""
import numpy as np


def main():
    m = np.array([[1, -2, 3], [0, 4, 5], [7, 8, -9]])
    print("m:", m, sep="\n", end="\n\n")
    print("m transposed:", m.T, sep="\n", end="\n\n")
    print("m inverse:", np.linalg.inv(m), sep="\n", end="\n\n")

    v = np.array([[2], [3], [4]])
    print("v:", v)
    print("m * v:", m * v, end="\n\n")

    print("determinant:", np.linalg.det(m))
    print("eigenvalues:", np.linalg.eigvals(m))

    x = np.linalg.solve(m, v)
    print("solve for x in mx = v:\n", x)
    print("m * x:\n", m * x)


if __name__ == "__main__":
    main()
