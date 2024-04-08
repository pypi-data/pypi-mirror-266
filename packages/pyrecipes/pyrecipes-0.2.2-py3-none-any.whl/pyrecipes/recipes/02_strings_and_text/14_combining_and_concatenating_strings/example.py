"""
You want to combine many small strings together into a larger string.
"""


def main():
    parts = ["Is", "Chicago", "Not", "Chicago?"]
    print(parts)
    for sep in [" ", ",", ""]:
        print(sep.join(parts))

    a = "Is Chicago"
    b = "Not Chicago?"
    print("a:", a)
    print("b:", b)
    print(a + " " + b)

    a = "hello" "world"
    print(a)


if __name__ == "__main__":
    main()
