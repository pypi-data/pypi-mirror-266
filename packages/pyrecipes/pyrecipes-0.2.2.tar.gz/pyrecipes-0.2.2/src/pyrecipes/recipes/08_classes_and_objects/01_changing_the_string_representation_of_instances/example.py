"""
You want to change the output produced by printing or viewing instances
to something more sensible.
"""


class Pair:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Pair({0.x!r}, {0.y!r})".format(self)

    def __str__(self):
        return "({0.x!s}, {0.y!s})".format(self)


def main():
    p = Pair(3, 4)
    print(p)
    print(p.__repr__())


if __name__ == "__main__":
    main()
