"""
You want to optionally enforce type checking of function arguments
as a kind of assertion or contract.
"""

from inspect import signature
from functools import wraps


def typeassert(*ty_args, **ty_kwargs):
    def decorate(func):
        # If in optimized mode disable type-checking
        if not __debug__:
            return func

        # Map function argument names to supplied types
        sig = signature(func)
        bound_types = sig.bind_partial(*ty_args, **ty_kwargs).arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs)

            # Enforce type assertions across supplied arguments
            for name, value in bound_values.arguments.items():
                if name in bound_types:
                    if not isinstance(value, bound_types[name]):
                        raise TypeError(f"Argument {name} must be {bound_types[name]}")
            return func(*args, **kwargs)

        return wrapper

    return decorate


@typeassert(int, int)
def add(a, b):
    return a + b


@typeassert(int, z=str)
def spam(x, y, z):
    return f"{'SPAM! ' * x} - y: {y} - filed by {z}"


def main():
    print(add(1, 2))

    try:
        print(add(1, "a"))
    except TypeError as exc:
        print(f"Caught error: {exc}")

    print(spam(3, 2, "Chris"))

    try:
        print(spam(3, 2, 9.0))
    except TypeError as exc:
        print(f"Caught error: {exc}")


if __name__ == "__main__":
    main()
