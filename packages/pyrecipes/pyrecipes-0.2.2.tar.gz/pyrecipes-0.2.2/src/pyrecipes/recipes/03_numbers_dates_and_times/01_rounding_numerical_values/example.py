"""
You want to round a floating-point number to a fixed numer or decimal place
"""


def example_1():
    x = 1.234567
    print(f"x:\n  {x}\n")
    print(f"rounded 1 decimal place:\n  {round(x, 1)}\n")
    print(f"rounded 3 decimal place:\n  {round(x, 3)}\n")


def example_2():
    x = 1627731
    print(f"x:\n {x}\n")
    print(f"rounded to nearest 10s:\n  {round(x, -1)}\n")
    print(f"rounded to nearest 100s:\n  {round(x, -2)}\n")
    print(f"rounded to nearest 1000s:\n  {round(x, -3)}\n")


def main():
    example_1()
    print("=" * 50)
    example_2()


if __name__ == "__main__":
    main()
