"""
You've written a function, but would like to attach some additional
information to the arguments so that others know more about how a
function is supposed to be used.
"""

import pydoc


def add(x: int, y: int):
    """Adds 2 integers"""
    return x + y


def main():
    x = 2
    y = 3
    print(f"x: {x}, y: {y}")
    print(pydoc.render_doc(add))
    print(add(x, y))
    print(add.__annotations__)


if __name__ == "__main__":
    main()
