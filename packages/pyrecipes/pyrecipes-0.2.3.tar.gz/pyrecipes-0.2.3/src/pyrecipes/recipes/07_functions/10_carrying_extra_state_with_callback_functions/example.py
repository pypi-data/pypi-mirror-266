"""
You're writing code that relies on the use of callback functions
(e.g. even handlers, completion callbacks, etc.), but you want to
have the callback function carry extra state for use inside the
callback function.
"""


def apply_async(func, args, *, callback):
    # Compute the result
    result = func(*args)

    # Invoke the callback with the result
    callback(result)


def print_result(result):
    print("Got:", result)


def add(x, y):
    return x + y


class ResultHandler:
    def __init__(self):
        self.sequence = 0

    def handler(self, result):
        self.sequence += 1
        print(f"[{self.sequence}] Got: {result}")


def example_1():
    """Callback only accepts a single result - no other info is passed."""
    print(example_1.__doc__)
    apply_async(add, (1, 2), callback=print_result)
    apply_async(add, ("Hello ", "World!"), callback=print_result)
    print()


def examlpe_2():
    """Callback is a bound method now - additional state can be passed."""
    r = ResultHandler()
    print(examlpe_2.__doc__)
    apply_async(add, (1, 2), callback=r.handler)
    apply_async(add, ("Hello ", "World!"), callback=r.handler)
    print()


def main():
    example_1()
    examlpe_2()


if __name__ == "__main__":
    main()
