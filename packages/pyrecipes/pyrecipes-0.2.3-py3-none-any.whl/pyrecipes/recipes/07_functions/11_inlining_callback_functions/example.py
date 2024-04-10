"""
You're writing code that uses callback functions, but you're concerned
about the proliferation of small functions and mind-boggling control
flow. You would like some way to make the code look more like a sequence
of procedural steps.
"""
from queue import Queue
from functools import wraps


def apply_async(func, args, *, callback):
    # Compute the result
    result = func(*args)

    # Invoke the callback with the result
    callback(result)


def add(x, y):
    return x + y


def inlined_async(func):
    @wraps(func)
    def wrapper(*args):
        f = func(*args)
        result_queue = Queue()
        result_queue.put(None)

        while True:
            result = result_queue.get()
            try:
                a = f.send(result)
                apply_async(a.func, a.args, callback=result_queue.put)
            except StopIteration:
                break

    return wrapper


class Async:
    def __init__(self, func, args):
        self.func = func
        self.args = args


@inlined_async
def example_1():
    r = yield Async(add, (2, 3))
    print(r)
    r = yield Async(add, ("Hello ", "World!"))
    print(r)

    for n in range(10):
        r = yield Async(add, (n, n))
        print(r)
    print("Goodbye")


def main():
    example_1()


if __name__ == "__main__":
    main()
