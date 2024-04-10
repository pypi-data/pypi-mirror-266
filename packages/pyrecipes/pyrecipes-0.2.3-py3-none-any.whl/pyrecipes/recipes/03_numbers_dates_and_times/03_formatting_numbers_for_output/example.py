"""
You need to format numbers for output, controlling the number of digits,
alignment, inclusion of thousands separator, and other details.
"""


def main():
    """
    General pattern for format is:
        '[<>^]?width[,]?(.digits)?'
    Where width and digits are integers and ? signifies optional parts.
    """
    x = 1234.56789

    print("Two decimal places of accuracy:")
    print(format(x, "0.2f"))

    print("\nRight justified in 10-chars, one-digit accuracy:")
    print(format(x, ">10.1f"))

    print("\nLeft justified")
    print(format(x, "<10.1f"))

    print("\nCentered")
    print(format(x, "^10.1f"))

    print("\nInclusion of thousand separator:")
    print(format(x, ","))
    print(format(x, "0,.1f"))

    print("\nExponential notation:")
    print(format(x, "e"))
    print(format(x, "0.2E"))


if __name__ == "__main__":
    main()
