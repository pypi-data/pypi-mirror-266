"""
You want to find the largest of smallest N items in a collection.
"""

import heapq
from pprint import pprint


def example_1():
    nums = [1, 8, 2, 23, 7, -4, 18, 23, 42, 37, 2]
    print(f"Nums: {nums}")
    print(f"Largest 3: {heapq.nlargest(3, nums)}")
    print(f"Smallest 3: {heapq.nsmallest(3, nums)}")


def example_2():
    portfolio = [
        {"name": "IBM", "shares": 100, "price": 91.1},
        {"name": "AAPL", "shares": 50, "price": 543.22},
        {"name": "FB", "shares": 200, "price": 21.09},
        {"name": "HPQ", "shares": 35, "price": 31.75},
        {"name": "YHOO", "shares": 45, "price": 16.35},
        {"name": "ACME", "shares": 75, "price": 115.65},
    ]
    print("portfolio")
    pprint(portfolio)
    print("\n3 cheapest stocks:")
    pprint(heapq.nsmallest(3, portfolio, key=lambda x: x["price"]))
    print("\n3 most expensive stocks:")
    pprint(heapq.nlargest(3, portfolio, key=lambda x: x["price"]))


def main():
    example_1()
    print("=" * 50)
    example_2()


if __name__ == "__main__":
    main()
