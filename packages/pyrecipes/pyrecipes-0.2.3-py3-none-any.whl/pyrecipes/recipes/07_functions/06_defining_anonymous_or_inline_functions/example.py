"""
You need to supply a short callback function for use with an operation
such as sort(), but you don't want to write separate one-line function
using the def statement. Instead you'd like a shortcut that allows you
to specify the function "in line".
"""


def main():
    add = lambda x, y: x + y
    print(add(2, 3))
    print(add("Hello ", "World!"))

    names = ["David Beazley", "Brian Jones", "Raymond Hattinger", "Ned Batchelder"]
    print("names:", names)
    print("sorted names:", sorted(names, key=lambda x: x.split()[-1].lower()))


if __name__ == "__main__":
    main()
