"""
Your code for interacting with the latest web authentication schema
has encountered a singularity and your only solution is to go around
it in the complex plane. Or maybe you just need to perform some
calculations using complex number.
"""
import cmath


def main():
    a = complex(2, 4)
    b = 3 - 5j
    print(a, b)
    print(a.real, a.imag, a.conjugate())
    print(a + b)
    print(cmath.sqrt(-1))
    print(cmath.sin(a))
    print(cmath.cos(a))
    print(cmath.exp(a))


if __name__ == "__main__":
    main()
