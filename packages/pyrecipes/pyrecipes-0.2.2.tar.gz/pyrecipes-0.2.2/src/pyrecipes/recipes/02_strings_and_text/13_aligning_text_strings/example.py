"""
You need to format text with some sort of alignment applied.
"""


def main():
    text = "Hello World"
    print(text)
    print(text.ljust(20))
    print(text.rjust(20))
    print(text.center(20))
    print(text.rjust(20, "="))
    print(text.center(20, "*"))
    print(format(text, ">20"))
    print(format(text, "=>20"))


if __name__ == "__main__":
    main()
