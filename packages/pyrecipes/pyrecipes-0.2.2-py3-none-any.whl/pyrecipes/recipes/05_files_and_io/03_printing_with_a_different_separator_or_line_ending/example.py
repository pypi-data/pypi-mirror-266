"""
You want to print data using print(), but you also want to change the separator
character or line ending.
"""


def main():
    print("ACME", 50, 91.5)
    print("ACME", 50, 91.5, sep=",")
    print("ACME", 50, 91.5, sep=",", end="!!\n")
    for i in range(5):
        print(i, end=" ")


if __name__ == "__main__":
    main()
