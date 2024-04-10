"""
You have a class that only defines a single method besides __init__().
However, to simplify your code, you would much rather just have a simple function.
"""


class URLTemplate:
    def __init__(self, template):
        self.template = template

    def open(self, **kwargs):
        return self.template.format_map(kwargs)


def urltemplate(template):
    def opener(**kwargs):
        return template.format_map(kwargs)

    return opener


def main():
    # Example usage of the class method
    yahoo = URLTemplate("http://finance.yahoo.com/d/quotes.csv?s={names}&f={fields}")
    print(yahoo.open(names="IBM,AAPL,FB", fields="sl1c1v"))

    # Replacing the class with a function using closures
    yahoo = urltemplate("http://finance.yahoo.com/d/quotes.csv?s={names}&f={fields}")
    print(yahoo(names="IBM,AAPL,FB", fields="sl1c1v"))


if __name__ == "__main__":
    main()
