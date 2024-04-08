"""
You need to execute a reduction function (e.g. sum(), min(), max()), but first need
to transform or filter the data.
"""


def main():
    # Output a tuple as CSV
    s = ("ACME", 50, 123.45)
    print(",".join(str(x) for x in s))

    # Data reduction across fields of a data structure
    portfolio = [
        {"name": "GOOG", "shares": 50},
        {"name": "YHOO", "shares": 75},
        {"name": "AOL", "shares": 20},
        {"name": "SCOX", "shares": 65},
    ]
    min_shares = min(s["shares"] for s in portfolio)
    print(min_shares)


if __name__ == "__main__":
    main()
