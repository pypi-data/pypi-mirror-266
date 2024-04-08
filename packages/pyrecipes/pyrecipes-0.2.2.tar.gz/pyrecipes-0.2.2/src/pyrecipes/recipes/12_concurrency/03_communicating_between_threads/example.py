"""
You have multiple threads in your program and you want
to safely communicate or exchange data between them.
"""

import random
import threading
import heapq
from queue import Queue
from threading import Thread

_sentinel = object()


def producer(out_q):
    """A thread that produces data."""
    random.seed(2023)
    while True:
        # Produce some data ...
        data = random.randint(1, 100)
        out_q.put(data)
        print(f"produced: {data}")
        if data >= 95:
            print("Stopping.")
            out_q.put(_sentinel)
            break


def consumer(in_q):
    """A thread that consumes data"""
    while True:
        # Get some data
        data = in_q.get()

        if data is _sentinel:
            in_q.put(_sentinel)
            print("Stopping")
            break

        # Do some processing...
        print(f"consumed: {data}")


class ThreadSafePriorityQueue:
    def __init__(self) -> None:
        self._queue = []
        self._count = 0
        self._cv = threading.Condition()

    def put(self, item, priority):
        with self._cv:
            heapq.heappush(self._queue, (-priority, self._count, item))
            self._count += 1
            self._cv.notify()

    def get(self):
        with self._cv:
            while len(self._queue) == 0:
                self._cv.wait()
            return heapq.heappop(self._queue)[-1]


def example_1():
    q = Queue()
    t1 = Thread(target=consumer, args=(q,))
    t2 = Thread(target=producer, args=(q,))
    t1.start()
    t2.start()


def main():
    example_1()


if __name__ == "__main__":
    main()
