"""
You have an N-element tuple or sequence that you want to
unpack into a collection of N variables.
"""


def main():
    p = (4, 5)
    print("p:", p)

    x, y = p
    print(x, y)

    data = ["ACME", 50, 9.1, (2012, 12, 21)]
    print("data:", data)
    name, shares, price, date = data
    print("name:", name)
    print("shares:", shares)
    print("price:", price)
    print("date:", date)


if __name__ == "__main__":
    main()
