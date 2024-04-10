"""
You have a sequence of dictionaries or instances and you want to iterate over the
data in groups based on the value of a particular field, such as date.
"""

from operator import itemgetter
from itertools import groupby
from pprint import pprint


def main():
    rows = [
        {"address": "5412 N CLARK", "date": "07/01/2012"},
        {"address": "5148 N CLARK", "date": "07/04/2012"},
        {"address": "5800 E 58TH", "date": "07/02/2012"},
        {"address": "2122 N CLARK", "date": "07/03/2012"},
        {"address": "5645 N RAVENSWOOD", "date": "07/02/2012"},
        {"address": "1060 W ADDISON", "date": "07/02/2012"},
        {"address": "4801 N BROADWAY", "date": "07/01/2012"},
        {"address": "1039 W GRANVILLE", "date": "07/04/2012"},
    ]

    print("Original rows:")
    pprint(rows)

    # Sort first by the desired field
    rows.sort(key=itemgetter("date"))
    print("\nRows - sorted by date")
    pprint(rows)

    # Iterate over groups
    print("\nIterating over groups (grouped by date)")
    for date, items in groupby(rows, key=itemgetter("date")):
        print(f"Date: {date}")
        for item in items:
            print(f"  {item}")
        print()


if __name__ == "__main__":
    main()
