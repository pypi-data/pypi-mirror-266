"""
You want to iterate over a sequence, but would like to keep track of which
element of the sequence is currently being processed.
"""


def main():
    my_list = ["a", "b", "c"]

    print(f"my_list: {my_list}")
    print("enumerating - default")
    for idx, val in enumerate(my_list):
        print(idx, val)

    print("enumerating - idx stars at 1")
    for idx, val in enumerate(my_list, 1):
        print(idx, val)


if __name__ == "__main__":
    main()
