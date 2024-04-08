"""
You want to implement a custom iteration pattern that's different
than the usual built-in functions (e.g. range(), reversed(), etc.)
"""


def frange(start, stop, increment):
    x = start
    while x < stop:
        yield x
        x += increment


def countdown(n):
    while n > 0:
        yield n
        n -= 1


def main():
    print("For loop - starting at 0, ending at 4 and incrementing by 0.5")
    for x in frange(0, 4, 0.5):
        print(x)

    print("\nList of valuee between 0 and 1 with a 0.125 increment")
    print(list(frange(0, 1, 0.125)))

    print("\nCounting down from 5")
    for x in countdown(5):
        print(x)
    print("Done!\n")

    print(f"list of values from the countdown: {list(countdown(5))}")


if __name__ == "__main__":
    main()
