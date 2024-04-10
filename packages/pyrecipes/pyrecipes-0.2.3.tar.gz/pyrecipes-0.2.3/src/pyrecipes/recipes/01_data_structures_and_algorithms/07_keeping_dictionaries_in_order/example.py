"""
You want to create a dictionary, and you also want to control
the order of items when iterating or serializing.
"""
from collections import OrderedDict
import json


def main():
    d = OrderedDict()
    d["foo"] = 1
    d["bar"] = 2
    d["spam"] = 3
    d["grok"] = 4

    for key, val in d.items():
        print(key, val)

    print(json.dumps(d))


if __name__ == "__main__":
    main()
