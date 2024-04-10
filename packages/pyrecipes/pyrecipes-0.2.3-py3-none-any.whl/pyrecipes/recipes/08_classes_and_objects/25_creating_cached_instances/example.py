"""
When creating instances of a class, you want to return a cached reference
to a previous instance created with the same arguments (if any).
"""


def example_1():
    # Simple example
    class Spam:
        def __init__(self, name):
            self.name = name

    # Caching support
    import weakref

    _spam_cache = weakref.WeakValueDictionary()

    def get_spam(name):
        if name not in _spam_cache:
            s = Spam(name)
            _spam_cache[name] = s
        else:
            s = _spam_cache[name]
        return s

    a = get_spam("foo")
    b = get_spam("bar")
    print("a is b:", a is b)
    c = get_spam("foo")
    print("a is c:", a is c)
    print()


def example_2():
    import weakref

    class CachedSpamManager:
        def __init__(self):
            self._cache = weakref.WeakValueDictionary()

        def get_spam(self, name):
            if name not in self._cache:
                s = Spam(name)
                self._cache[name] = s
            else:
                s = self._cache[name]
            return s

    class Spam:
        def __init__(self, name):
            self.name = name

    Spam.manager = CachedSpamManager()

    def get_spam(name):
        return Spam.manager.get_spam(name)

    a = get_spam("foo")
    b = get_spam("bar")
    print("a is b:", a is b)
    c = get_spam("foo")
    print("a is c:", a is c)
    print()


def example_3():
    # Example involving new and some of its problems
    import weakref

    class Spam:
        _spam_cache = weakref.WeakValueDictionary()

        def __new__(cls, name):
            if name in cls._spam_cache:
                return cls._spam_cache[name]
            else:
                self = super().__new__(cls)
                cls._spam_cache[name] = self
                return self

        def __init__(self, name):
            print("Initializing Spam")
            self.name = name

    print("This should print 'Initializing Spam' twice")
    s = Spam("Dave")
    t = Spam("Dave")
    print(s is t)


def main():
    example_1()
    example_2()
    example_3()


if __name__ == "__main__":
    main()
