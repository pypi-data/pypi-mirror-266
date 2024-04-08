"""
You want to define a class that serves as an interface or abstract base
class from which you can perform type checking and ensure certain methods
are implemented in subclasses.
"""
from abc import ABCMeta, abstractmethod


class IStream(metaclass=ABCMeta):
    @abstractmethod
    def read(self, maxbytes=-1):
        pass

    @abstractmethod
    def write(self, data):
        pass


class Socket(IStream):
    def read(self, maxbytes=-1):
        ...

    def write(self, data):
        ...


def serialize(obj, stream):
    if not isinstance(stream, IStream):
        raise TypeError("Expected an IStream")
    print("obj is an IStream - serializing...")


def main():
    try:
        IStream()
    except TypeError as exc:
        print(exc)

    socket = Socket()
    print(socket)
    serialize("somefile.text", socket)


if __name__ == "__main__":
    main()
