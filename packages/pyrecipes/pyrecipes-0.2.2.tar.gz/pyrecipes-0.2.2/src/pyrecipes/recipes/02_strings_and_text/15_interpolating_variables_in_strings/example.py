"""
You want to create a string in which embedded variable names are substituted
with a string representation of a variables value.
"""
import sys


class Info:
    def __init__(self, name, n):
        self.name = name
        self.n = n

    def __str__(self) -> str:
        return f"Info(name={self.name}, n={self.n})"


class safesub(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def sub(text: str):
    return text.format_map(safesub(sys._getframe(1).f_locals))


def main():
    s = "{name} has {n} messages."
    print(s)
    print(s.format(name="Guido", n=37))

    name = "Guido"
    n = 37
    print(s.format_map(vars()))

    a = Info("Guido", 37)
    print(a)
    print(s.format_map(vars(a)))

    try:
        s.format(name="Guido")
    except KeyError as exc:
        print(exc.__class__, exc)

    del n

    print(s.format_map(safesub(vars())))

    name = "Guido"
    n = 37

    print(sub(f"Hello {name}"))
    print(sub(f"You have {n}"))
    print(sub("Your favourite color is {color}"))


if __name__ == "__main__":
    main()
