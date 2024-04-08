"""
A decorator has been applied to a function, but you want to 'undo' it,
gaining access to the original unwrapped function.
"""
from functools import wraps
import time


def somedecorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        print(
            f'Invoking the function "{func.__name__}" with\n  args: {args}\n  kwargs: {kwargs}'
        )
        result = func(*args, **kwargs)
        print(f"Got result {result} in {time.time() - start: .5f} seconds")

    return wrapper


@somedecorator
def add(a: int, b: int):
    return a + b


def main():
    print("Running withthe decorator as normal:")
    result = add(2, 3)
    print(result)

    print("\nunwrapping to run original function:")
    result = add.__wrapped__(2, 3)
    print(result)


if __name__ == "__main__":
    main()
