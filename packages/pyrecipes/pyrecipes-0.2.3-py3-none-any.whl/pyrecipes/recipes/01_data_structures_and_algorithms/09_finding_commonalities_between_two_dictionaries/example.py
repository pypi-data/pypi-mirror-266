"""
You have 2 dictionaries and want to find out what they might have in common (keys, values etc)
"""

from pprint import pprint

d1 = {"x": 1, "y": 2, "z": 3}

d2 = {"w": 10, "x": 11, "y": 2}


def main():
    print("Dict 1:")
    pprint(d1)
    print("\nDict 2:")
    pprint(d2)
    print(f"\nCommon keys:\n  {d1.keys() & d2.keys()}")
    print(f"Keys in dict 1 that are not in dict 2:\n  {d1.keys() - d2.keys()}")
    print(f"(key, value) pairs in common:\n  {d1.items() & d2.items()}")


if __name__ == "__main__":
    main()
