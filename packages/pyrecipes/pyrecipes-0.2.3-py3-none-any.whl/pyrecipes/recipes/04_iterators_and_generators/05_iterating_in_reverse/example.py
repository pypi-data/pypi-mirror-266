"""
You want to iterate in reverse over a sequence.
"""


class Countdown:
    def __init__(self, start):
        self.start = start

    # Forward iterator
    def __iter__(self):
        n = self.start
        while n > 0:
            yield n
            n -= 1

    # Reverse iterator
    def __reversed__(self):
        n = 1
        while n <= self.start:
            yield n
            n += 1


def main():
    c = Countdown(5)
    print("Forward:")
    for x in c:
        print(x)

    print("Reverse:")
    for x in reversed(c):
        print(x)


if __name__ == "__main__":
    main()
