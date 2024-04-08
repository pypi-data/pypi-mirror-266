"""
You want to match or search text for a specific pattern.
"""

import re


def main():
    # Some sample text
    text = "Today is 11/27/2012. PyCon starts 3/13/2013."

    # (a) Find all matching dates
    datepat = re.compile(r"\d+/\d+/\d+")
    print(datepat.findall(text))

    # (b) Find all matching dates with capture groups
    datepat = re.compile(r"(\d+)/(\d+)/(\d+)")
    for month, day, year in datepat.findall(text):
        print("{}-{}-{}".format(year, month, day))

    # (c) Iterative search
    for m in datepat.finditer(text):
        print(m.groups())


if __name__ == "__main__":
    main()
