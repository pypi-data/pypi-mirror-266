"""
You want to read an XML document, make changes to it, and then
write it back out as XML
"""
import sys
from xml.etree.ElementTree import parse, Element
from pathlib import Path


def main():
    with open(Path(__file__).parent / "pred.xml", "r") as f:
        doc = parse(f)
        print(doc)
    root = doc.getroot()
    print(root)

    # Remove a few elements
    root.remove(root.find("sri"))
    root.remove(root.find("cr"))

    # Insert a new element after <nm>...</nm>
    idx = list(root).index(root.find("nm"))
    print(idx)

    e = Element("spam")
    e.text = "This is a test"
    root.insert(idx + 1, e)

    # Write to stdout
    doc.write(sys.stdout.buffer, xml_declaration=True)


if __name__ == "__main__":
    main()
