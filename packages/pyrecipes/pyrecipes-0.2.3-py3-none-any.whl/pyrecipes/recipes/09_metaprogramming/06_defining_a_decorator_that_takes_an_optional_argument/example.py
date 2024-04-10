"""
You would like to write a single decorator that can be used without arguments,
such as @decorator, or with optional arguments, such as @decorator(x, y, z).
However, there seems to be no straightforward way to do it due to differences
in calling conventions between simple decorators and decorators taking arguments.
"""

from functools import wraps, partial
import logging


def logged(func=None, *, level=logging.DEBUG, name=None, message=None):
    if func is None:
        return partial(logged, level=level, message=message)
    logname = name if name else func.__module__
    log = logging.getLogger(logname)
    logmsg = message if message else func.__name__

    @wraps(func)
    def wrapper(*args, **kwargs):
        log.log(level, logmsg)
        return func(*args, **kwargs)

    return wrapper


@logged
def add(x, y):
    return x + y


@logged(level=logging.CRITICAL, name="spam", message="UH OH! Theres SPAM!")
def spam():
    return "SPAM!"


def main():
    logging.basicConfig(level=logging.DEBUG)
    print(add(1, 2))
    print(spam())


if __name__ == "__main__":
    main()
