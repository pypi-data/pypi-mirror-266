"""
You want to perform various calculations (e.g. minimum value,
maximum value, sorting etc.) on a dictionary pf data.
"""


def main():
    prices = {"ACME": 45.23, "AAPL": 612.78, "IBM": 205.55, "HPQ": 37.20, "FB": 10.75}
    print("prices:", prices)

    min_price = min(zip(prices.values(), prices))
    print("min_price:", min_price)

    max_price = max(zip(prices.values(), prices))
    print("max_price:", max_price)

    prices_sorted = sorted(zip(prices.values(), prices))
    print("prices_sorted:", prices_sorted)


if __name__ == "__main__":
    main()
