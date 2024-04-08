"""
You need to parse an XML document, but it's using XML namespaces.
"""
from pathlib import Path
from xml.etree.ElementTree import parse


class XMLNamespaces:
    def __init__(self, **kwargs):
        self.namespaces = {}
        for name, uri in kwargs.items():
            self.register(name, uri)

    def register(self, name, uri):
        self.namespaces[name] = "{" + uri + "}"

    def __call__(self, path):
        return path.format_map(self.namespaces)


def main():
    with open(Path(__file__).parent / "sample.xml", "r") as f:
        doc = parse(f)
    ns = XMLNamespaces(html="http://www.w3.org/1999/xhtml")

    e = doc.find(ns("content/{html}html"))
    print(e)

    text = doc.findtext(ns("content/{html}html/{html}head/{html}title"))
    print(text)


if __name__ == "__main__":
    main()
