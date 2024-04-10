"""
You want an object to support customized formatting through the format()
function and string method.
"""

_formats = {
    "ymd": "{d.year}-{d.month}-{d.day}",
    "mdy": "{d.month}/{d.day}/{d.year}",
    "dmy": "{d.day}/{d.month}/{d.year}",
}


class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    def __format__(self, code):
        code = "ymd" if code == "" else code
        fmt = _formats[code]
        return fmt.format(d=self)


def main():
    d = Date(2012, 12, 21)
    print(d)
    print(format(d, "ymd"))
    print(format(d, "mdy"))
    print(format(d, "dmy"))
    print("The date is {date}".format(date=d))
    print("The date is {date:mdy}".format(date=d))
    print("The date is {date:dmy}".format(date=d))


if __name__ == "__main__":
    main()
