"""
Your program creates a large number (e.g. millions) of instances
and uses a large amount of memory.
"""


class Date:
    __slots__ = ["year", "month", "day"]

    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day


def main():
    d = Date(2023, 1, 1)
    print(d)
    print(d.__slots__)
    print(d.year)
    print(d.month)
    print(d.day)


if __name__ == "__main__":
    main()
