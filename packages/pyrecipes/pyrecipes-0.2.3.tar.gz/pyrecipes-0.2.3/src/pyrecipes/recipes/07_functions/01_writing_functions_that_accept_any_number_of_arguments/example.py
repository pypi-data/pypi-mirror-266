"""
You want to write a function that accepts any number of input arguments.
"""

import html


def avg(first, *rest):
    return (first + sum(rest)) / (1 + len(rest))


def make_element(name, value, **attrs):
    attr_string = "".join(f' {k}="{v}"' for k, v in attrs.items())
    return f"<{name}{attr_string}>{html.escape(value)}</{name}>"


def anyargs(*args, **kwargs):
    return f"args: {args}\nkwargs: {kwargs}"


def main():
    print(f"avg(1, 2): {avg(1, 2)}")
    print(f"avg(1, 2, 3, 4): {avg(1, 2, 3, 4)}")

    print(make_element("item", "Albatross", size="large", quantity=6))
    print(make_element("p", "<spam>"))

    print(anyargs(1, 2, 3, a=4, b=5, c=6))


if __name__ == "__main__":
    main()
