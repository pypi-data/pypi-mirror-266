"""
You want to write a decorator that takes arguments.
"""
from functools import wraps
import logging


def logged(level, name=None, message=None):
    """
    Add logging to a function. level is the logging level,
    name is the logger name and message is the log message.
    If name and message aren't specified, they default to
    the function's module and name.
    """

    def decorate(func):
        logname = name if name else func.__module__
        log = logging.getLogger(logname)
        logmsg = message if message else func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            log.log(level, logmsg)
            return func(*args, **kwargs)

        return wrapper

    return decorate


@logged(logging.INFO)
def add(a, b):
    return a + b


@logged(logging.CRITICAL, message="example message")
def spam():
    print("this is spam")


def main():
    print("Example 1: @logged(logging.INFO)")
    add(1, 2)

    print(
        "\nExample 2: @logged(logging.CRITICAL, name='SPAM!', message='example message')"
    )
    spam()


if __name__ == "__main__":
    main()
