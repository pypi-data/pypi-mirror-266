"""
You have code that accesses list or tuple elements by position, but this
makes the code difficult to read at time. You'd also like to be less
dependent on position in the structure, by accessing the elements by name.
"""

from collections import namedtuple


def example_1():
    Subscriber = namedtuple("Subscriber", ["email", "joined"])
    print(f"Subscriber named tuple: {Subscriber}")

    sub = Subscriber(email="test@email.com", joined="2023-01-01")
    print(f"sub object: {sub}")
    print(f"email: {sub.email}")
    print(f"joined: {sub.joined}")


def example_2():
    Stock = namedtuple("Stock", ["name", "shares", "price"])

    def compute_cost(records):
        result = 0.0
        for record in records:
            s = Stock(*record)
            print(s)
            result += s.shares * s.price
        return result

    records = [("FB", 10, 12.30), ("MSFT", 20, 101.50), ("AAPL", 15, 120.23)]

    print(f"records: {records}")
    print(compute_cost(records))


def example_3():
    def dict_to_stock(d):
        return stock_prototype._replace(**d)

    Stock = namedtuple("Stock", ["name", "shares", "price", "date", "time"])
    stock_prototype = Stock("", 0, 0.0, None, None)
    print(f"Stock prototype: {stock_prototype}")

    d = {"name": "ACME", "shares": 100, "price": 123.45}
    print(f"dictionary value: {d}")
    print(f"dict to stock: {dict_to_stock(d)}")


def main():
    example_1()
    print("=" * 50)
    example_2()
    print("=" * 50)
    example_3()


if __name__ == "__main__":
    main()
