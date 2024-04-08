"""
You need to convert or output integers represented by binary, octal
or hexidecimal integers.
"""


def example_1():
    x = 1234
    print("x:", x)

    print("\nbin:", bin(x))
    print("alt:", format(x, "b"))

    print("\noct:", oct(x))
    print("alt:", format(x, "o"))

    print("\nhex:", hex(x))
    print("alt:", format(x, "x"))
    print("=" * 20)


def example_2():
    x = -1234
    print("x:", x)
    print("bin (signed)", format(x, "b"))
    print("hex (signed)", format(x, "x"))
    print("\n32-bit unsigned bin:", format(2**32 + x, "b"))
    print("32-bit unsigned hex:", format(2**32 + x, "x"))
    print("=" * 20)


def example_3():
    val = "4d2"
    print("val:", val)
    print("val as int:", int(val, 16))

    val = "10011010010"
    print("val:", val)
    print("val as int:", int(val, 2))


def main():
    example_1()
    example_2()
    example_3()


if __name__ == "__main__":
    main()
