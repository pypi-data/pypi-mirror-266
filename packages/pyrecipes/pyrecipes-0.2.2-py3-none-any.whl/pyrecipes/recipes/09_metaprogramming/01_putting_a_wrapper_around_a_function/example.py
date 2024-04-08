"""
You want to put a wrapper layer around a function that adds extra processing (e.g. logging, timing etc.)
"""
import time
from functools import wraps


def timethis(func):
    """
    Decorator that reports the execution time.
    """

    def wrapper(*args, **kwargs):
        """wrapped func"""
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end - start)
        return result

    return wrapper


def timethis_v2(func):
    """
    Decorator that reports the execution time.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """wrapped func"""
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end - start)
        return result

    return wrapper


@timethis
def countdown(n: int):
    """Counts down from n"""
    while n > 0:
        n -= 1


@timethis_v2
def countdown_v2(n: int):
    """Counts down from n"""
    while n > 0:
        n -= 1


def run(func, list_n):
    for n in list_n:
        func(n)
    print(f"function name: {func.__name__}")
    print(f"function docstring: {func.__doc__}")
    print(f"function annotations: {func.__annotations__}")


def main():
    print("Without preserving metadata...")
    run(countdown, [10, 1000, 1000000, 10000000])

    print("\nPreserving metadata... (with functools.wraps)")
    run(countdown_v2, [10, 1000, 1000000, 10000000])


if __name__ == "__main__":
    main()
