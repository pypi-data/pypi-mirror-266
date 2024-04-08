"""
You want to read or write data encoded as JSON (JavaScript Object Notation).
"""

import json
from pathlib import Path


def main():
    data = {"name": "AAPL", "shares": 10, "price": 100}
    print(data)

    json_str = json.dumps(data)
    data = json.loads(json_str)

    print(data)
    print(json_str)

    with open(Path(__file__).parent / "data.json", "r") as file:
        data = json.load(file)
    print(data)


if __name__ == "__main__":
    main()
