"""
You need to serialize a Python object into a byte stream so that
you can do things such as save it to a file, store it in a database,
or transmit it over a network connection.
"""
import pickle
from pathlib import Path
from fractions import Fraction
from decimal import Decimal


parent_dir = Path(__file__).parent


def main():
    # Some python object
    obj = [
        "A",
        "B",
        "C",
        (1, 2, 3),
        {1: [1, 2, 3.5], 2: ["a", "b", "c"]},
        Fraction(3, 16),
        Decimal("2.45"),
    ]
    print("obj:", obj)

    # "pickle" the object to a file
    with parent_dir.joinpath("pickled").open("wb") as f:
        pickle.dump(obj, f)

    # "pickle" to a string
    pickled_string = pickle.dumps(obj)
    print("pickle string:", pickled_string)

    # "unpickle" the object from a file
    with parent_dir.joinpath("pickled").open("rb") as f:
        unpickled = pickle.load(f)
        print("unpickeld file:", unpickled)

    # "unpickle" from string
    unpickled = pickle.loads(pickled_string)
    print("unpickled string:", unpickled)


if __name__ == "__main__":
    main()
