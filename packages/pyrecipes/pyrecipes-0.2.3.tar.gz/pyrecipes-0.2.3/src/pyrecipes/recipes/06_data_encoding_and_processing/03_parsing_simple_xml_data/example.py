"""
You would like to extract data from a simple XML document.
"""
from xml.etree.ElementTree import parse
from pathlib import Path


def example_1():
    # Download the RSS feed and parse it
    with open(Path(__file__).parent / "sample.xml", "r") as f:
        doc = parse(f)
        print(doc)

    # Extract and output tags of interest
    for item in doc.iterfind("channel/item"):
        title = item.findtext("title")
        date = item.findtext("pubDate")
        link = item.findtext("link")

        print(title)
        print(date)
        print(link)
        print()


def main():
    example_1()


if __name__ == "__main__":
    main()
