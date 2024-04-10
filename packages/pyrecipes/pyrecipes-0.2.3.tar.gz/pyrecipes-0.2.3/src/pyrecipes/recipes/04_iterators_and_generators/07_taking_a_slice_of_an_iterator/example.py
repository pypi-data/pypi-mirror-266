"""
You want to take a slice of data produced by an iterator, but the normal
slicing operator doesn't work.
"""

from itertools import islice


def count(n):
    while True:
        yield n
        n += 1


def main():
    print("Printing a slice of a generator function, 10-20")
    for x in islice(count(0), 10, 20):
        print(x)

    print("list slice from generator function")
    print(list(islice(count(0), 4, 12)))


if __name__ == "__main__":
    main()
