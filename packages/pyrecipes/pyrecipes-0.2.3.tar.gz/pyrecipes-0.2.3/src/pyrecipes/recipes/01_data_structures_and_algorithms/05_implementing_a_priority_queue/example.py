"""
You want to implement a priority queue that sorts items by a given priority and always returns
the item with the highest priority on each pop operation.
"""

import heapq


class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._index = 0

    def push(self, item, priority):
        heapq.heappush(self._queue, (-priority, self._index, item))
        self._index += 1

    def pop(self):
        return heapq.heappop(self._queue)[-1]

    def __repr__(self):
        return f"PriorityQueue({len(self._queue)} items)"

    @property
    def size(self):
        return len(self._queue)


class Item:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Item({self.name})"


def main():
    print("instantiating queue")
    q = PriorityQueue()
    print(q)
    items = [
        (Item("fourth"), 1),
        (Item("first"), 5),
        (Item("third"), 2),
        (Item("second"), 4),
    ]
    for item, priority in items:
        print(f"Adding item {item} with priority {priority}")
        q.push(item, priority)
    print(q)
    print("\npopping items in order of priority:")
    for i in range(q.size):
        item = q.pop()
        print(f"Popped {item}")


if __name__ == "__main__":
    main()
