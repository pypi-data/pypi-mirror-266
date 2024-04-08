"""
You have a collection of sorted sequences and you want to iterate over a sorted
sequence of them all merged together .
"""

import heapq


def main():
    a = [1, 4, 7, 10]
    b = [2, 5, 6, 11]
    c = [17, 23, 43, 86]

    print(f"a: {a}")
    print(f"b: {b}")
    print(f"c: {c}")
    print("merging and iterating into single sorted output:")
    for x in heapq.merge(a, b, c):
        print(x)


if __name__ == "__main__":
    main()
