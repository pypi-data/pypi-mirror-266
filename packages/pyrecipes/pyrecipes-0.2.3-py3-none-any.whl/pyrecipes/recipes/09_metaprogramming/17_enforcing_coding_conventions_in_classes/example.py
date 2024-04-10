"""
Your program consists of a large class hierarchy and you would like to
enforce certain kinds of coding conventions (or perform diagnostics) to
help maintain programmer sanity.
"""


def example_1():
    class NoMixedCaseMeta(type):
        def __new__(cls, clsname, bases, clsdict):
            for name in clsdict:
                if name.lower() != name:
                    raise TypeError("Bad attribute name: " + name)
            return super().__new__(cls, clsname, bases, clsdict)

    class Root(metaclass=NoMixedCaseMeta):
        pass

    class A(Root):
        def foo_bar(self):  # Ok
            pass

    print("**** About to generate a TypeError")
    try:

        class B(Root):
            def fooBar(self):  # TypeError
                pass

        B()

    except TypeError as exc:
        print(exc)


def example_2():
    from inspect import signature
    import logging

    class MatchSignaturesMeta(type):
        def __init__(self, clsname, bases, clsdict):
            super().__init__(clsname, bases, clsdict)
            sup = super(self, self)
            for name, value in clsdict.items():
                if name.startswith("_") or not callable(value):
                    continue
                # Get the previous definition (if any) and compare the signatures
                prev_dfn = getattr(sup, name, None)
                if prev_dfn:
                    prev_sig = signature(prev_dfn)
                    val_sig = signature(value)
                    if prev_sig != val_sig:
                        logging.warning(
                            "Signature mismatch in %s. %s != %s",
                            value.__qualname__,
                            str(prev_sig),
                            str(val_sig),
                        )

    # Example
    class Root(metaclass=MatchSignaturesMeta):
        pass

    class A(Root):
        def foo(self, x, y):
            pass

        def spam(self, x, *, z):
            pass

    # Class with redefined methods, but slightly different signatures
    class B(A):
        def foo(self, a, b):
            pass

        def spam(self, x, z):
            pass


def main():
    example_1()
    example_2()


if __name__ == "__main__":
    main()
