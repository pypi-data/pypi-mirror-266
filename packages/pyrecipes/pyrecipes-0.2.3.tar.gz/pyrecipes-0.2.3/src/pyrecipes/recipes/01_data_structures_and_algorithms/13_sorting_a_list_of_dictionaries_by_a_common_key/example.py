"""
You have a list of dictionaries and you would like to sort the
entries according to one or more of the dictionary values.
"""

from operator import itemgetter
from pprint import pprint


def main():
    rows = [
        {"fname": "Brian", "lname": "Jones", "uid": 1003},
        {"fname": "David", "lname": "Beazley", "uid": 1002},
        {"fname": "John", "lname": "Cleese", "uid": 1001},
        {"fname": "Big", "lname": "Jones", "uid": 1004},
    ]

    print("Rows:")
    pprint(rows)

    print("\nSorted by fname")
    pprint(sorted(rows, key=itemgetter("fname")))

    print("\nSorted by lname")
    pprint(sorted(rows, key=itemgetter("lname")))

    print("\nSorted by both lname & fname")
    pprint(sorted(rows, key=itemgetter("lname", "fname")))

    print("\nRecord with min id")
    pprint(min(rows, key=itemgetter("uid")))

    print("\nRecord with max uid")
    pprint(max(rows, key=itemgetter("uid")))


if __name__ == "__main__":
    main()
