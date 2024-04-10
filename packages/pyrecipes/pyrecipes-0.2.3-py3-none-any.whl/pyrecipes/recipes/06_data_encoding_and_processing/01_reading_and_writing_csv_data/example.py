"""
You want to read or write data encoded as a CSV file.
"""

import csv
from pathlib import Path
from collections import namedtuple


def example_1():
    with open(Path(__file__).parent / "stocks.csv", "r") as f:
        f_csv = csv.reader(f)
        print(f_csv)
        headers = next(f_csv)
        print(f"Header: {headers}")
        for i, row in enumerate(f_csv, 1):
            print(f"[{i:^3}] - {row}")


def example_2():
    with open(Path(__file__).parent / "stocks.csv", "r") as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)
        Row = namedtuple("Row", headers)
        print(headers)
        for r in f_csv:
            row = Row(*r)
            print(row)


def example_3():
    with open(Path(__file__).parent / "stocks.csv", "r") as f:
        f_csv = csv.DictReader(f)
        for r in f_csv:
            print(r)


def main():
    example_1()
    example_2()
    example_3()


if __name__ == "__main__":
    main()
