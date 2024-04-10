"""
You want to write a decorator function that wraps a function, but
has user adjustable attibutes that can be used to control the behavior
of the decorator at runtime.
"""

from functools import partial, wraps
import logging


# Utility decorator to attach a function as an attribute of obj
def attach_wrapper(obj, func=None):
    if func is None:
        return partial(attach_wrapper, obj)
    setattr(obj, func.__name__, func)
    return func


def logged(level, name=None, message=None):
    """Add logging to a function. level is the logging
    level, name is the logger name, message is the log
    message. If name and message aren't specified, they
    default to the functions module and name."""

    def decorate(func):
        logname = name if name else func.__module__
        log = logging.getLogger(logname)
        logmsg = message if message else func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            log.log(level, logmsg)
            return func(*args, **kwargs)

        @attach_wrapper(wrapper)
        def set_level(newlevel):
            nonlocal level
            level = newlevel

        @attach_wrapper(wrapper)
        def set_message(newmsg):
            nonlocal logmsg
            logmsg = newmsg

        return wrapper

    return decorate


@logged(logging.DEBUG)
def add(x, y):
    return x + y


@logged(logging.CRITICAL, "example")
def spam():
    print("Spam!")


def main():
    logging.basicConfig(level=logging.DEBUG)
    print(add(1, 2))
    add.set_message("Add was called.")
    print(add(2, 3))
    add.set_level(logging.WARN)
    print(add(3, 4))
    spam()


if __name__ == "__main__":
    main()
