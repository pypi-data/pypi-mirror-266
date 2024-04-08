"""
You launched a thread, but want to know when it actually starts running.
"""

import time
import threading
from threading import Thread, Event


def countdown(n, started_event):
    print("countdown started")
    started_event.set()
    while n > 0:
        print(f"T-minus {n}")
        n -= 1
        time.sleep(1)


def example_1():
    # Create the event object used to signal startup
    started_event = Event()

    # Launch the thread and pass the startup event
    print("Laumching countdown")
    t = Thread(target=countdown, args=(10, started_event), daemon=True)
    t.start()

    # Wait for the thread to start
    started_event.wait()
    print("Countdown is running")


def example_2():  # pragma: no cover
    class PeriodicTimer:
        def __init__(self, interval):
            self._interval = interval
            self._flag = 0
            self._cv = threading.Condition()

        def start(self):
            t = threading.Thread(target=self.run, daemon=True)
            t.start()

        def run(self):
            """
            Run the timer and notify waiting threads after each interval
            """
            while True:
                time.sleep(self._interval)
                with self._cv:
                    self._flag ^= 1
                    self._cv.notify_all()

        def wait_for_tick(self):
            """
            Wait for the next tick of the timer
            """
            with self._cv:
                last_flag = self._flag
                while last_flag == self._flag:
                    self._cv.wait()

    # Example use of the timer
    ptimer = PeriodicTimer(5)
    ptimer.start()

    # Two threads that synchronize on the timer
    def countdown(nticks):
        while nticks > 0:
            ptimer.wait_for_tick()
            print("T-minus", nticks)
            nticks -= 1

    def countup(last):
        n = 0
        while n < last:
            ptimer.wait_for_tick()
            print("Counting", n)
            n += 1

    threading.Thread(target=countdown, args=(10,)).start()
    threading.Thread(target=countup, args=(5,)).start()


def main():
    example_1()
    # example_2()


if __name__ == "__main__":
    main()
