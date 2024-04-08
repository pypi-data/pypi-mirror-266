"""
You want to write a decorator that adds an extra argument to the calling
signature of the wrapped function. However, the added argument can't
interfere with the existing calling conventions of the function.
"""

from functools import wraps


def optional_debug(func):
    @wraps(func)
    def wrapper(*args, debug=False, **kwargs):
        if debug:
            print("Calling", func.__name__)
        return func(*args, **kwargs)

    return wrapper


@optional_debug
def spam(a, b, c):
    print(a, b, c)


def main():
    spam(1, 2, 3)
    spam(1, 2, 3, debug=True)


if __name__ == "__main__":
    main()
