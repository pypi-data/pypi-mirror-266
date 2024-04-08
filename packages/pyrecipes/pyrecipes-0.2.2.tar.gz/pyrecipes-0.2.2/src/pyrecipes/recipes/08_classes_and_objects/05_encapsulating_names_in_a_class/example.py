"""
You want to encapsulate 'private' data on instances of a class,
but are concerned about Python's lack of access control.
"""


class A:
    def __init__(self):
        self._internal = 0  # An internal attribute
        self.public = 1  # A public attribute

    def public_method(self):
        """A public method"""
        print("public")

    def _internal_method(seld):
        """A private method"""
        print("private")


def main():
    a = A()
    print(a._internal)
    print(a.public)
    a._internal_method()
    a.public_method()


if __name__ == "__main__":
    main()
