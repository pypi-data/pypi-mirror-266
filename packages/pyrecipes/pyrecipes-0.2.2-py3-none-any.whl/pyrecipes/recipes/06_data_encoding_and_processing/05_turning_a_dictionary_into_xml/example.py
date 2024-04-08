"""
You want to take the data in a Python dictionary and turn it into XML.
"""
from xml.etree.ElementTree import Element, tostring


def dict_to_xml(tag, d):
    """Turn a simple dict of key/value pairs into XML"""
    elem = Element(tag)
    for key, val in d.items():
        child = Element(key)
        child.text = str(val)
        elem.append(child)
    return elem


def main():
    s = {"name": "GOOG", "shares": 100, "price": 490.1}
    print("s:", s)
    e = dict_to_xml("stock", s)
    print("e:", e)
    print("e to string:", tostring(e))

    # Set some attributes
    e.set("_id", "1234")
    print("e to string:", tostring(e))


if __name__ == "__main__":
    main()
