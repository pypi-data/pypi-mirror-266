"""
You want to create and destroy threads for concurrent execution of code.
"""

import time
from threading import Thread


class CountdownTask:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self, n):
        while self._running and n > 0:
            print("T-minus", n)
            n -= 1
            time.sleep(1)


def countdown(n):
    while n > 0:
        print("T-minus", n)
        n -= 1
        time.sleep(1)


def main():
    t = Thread(target=countdown, args=(10,), daemon=True)
    print(t)
    t.start()
    if t.is_alive():
        print("t is still running")
    else:
        print("t is finished")

    c = CountdownTask()
    t2 = Thread(target=c.run, args=(10,), daemon=True)
    t2.start()


if __name__ == "__main__":
    main()
