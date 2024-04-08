"""
You need to extract data from a huge XML document using as little memory as possible.
"""
from xml.etree.ElementTree import iterparse
from pathlib import Path
from collections import Counter


def parse_and_remove(filename, path):
    path_parts = path.split("/")
    doc = iterparse(filename, ("start", "end"))
    # Skip the root element
    next(doc)

    tag_stack = []
    elem_stack = []
    for event, elem in doc:
        if event == "start":
            tag_stack.append(elem.tag)
            elem_stack.append(elem)
        elif event == "end":
            if tag_stack == path_parts:
                yield elem
                elem_stack[-2].remove(elem)
            try:
                tag_stack.pop()
                elem_stack.pop()
            except IndexError:
                pass


def main():
    # Find zip code with most potholes
    potholes_by_zip = Counter()
    file = Path(__file__).parent / "potholes.xml"

    data = parse_and_remove(file, "row/row")
    for pothole in data:
        potholes_by_zip[pothole.findtext("zip")] += 1

    for zipcode, num in potholes_by_zip.most_common():
        print(zipcode, num)


if __name__ == "__main__":
    main()
