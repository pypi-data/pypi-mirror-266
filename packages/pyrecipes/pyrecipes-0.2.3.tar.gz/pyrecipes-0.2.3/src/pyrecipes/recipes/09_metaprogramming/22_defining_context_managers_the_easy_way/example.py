"""
You want to implement new kinds of context managers for use with the 'with' statement.
"""

import time
from contextlib import contextmanager


def example_1():
    @contextmanager
    def timethis(label):
        start = time.time()
        try:
            yield
        finally:
            end = time.time()
            print("{}: {}".format(label, end - start))

    # Example use
    with timethis("counting"):
        n = 10000000
        while n > 0:
            n -= 1


def example_2():
    @contextmanager
    def list_transaction(orig_list):
        working = list(orig_list)
        yield working
        orig_list[:] = working

    # Example
    items = [1, 2, 3]
    with list_transaction(items) as working:
        working.append(4)
        working.append(5)
    print(items)
    try:
        with list_transaction(items) as working:
            working.append(6)
            working.append(7)
            raise RuntimeError("oops")
    except RuntimeError as e:
        print(e)

    print(items)


def main():
    example_1()
    example_2()


if __name__ == "__main__":
    main()
