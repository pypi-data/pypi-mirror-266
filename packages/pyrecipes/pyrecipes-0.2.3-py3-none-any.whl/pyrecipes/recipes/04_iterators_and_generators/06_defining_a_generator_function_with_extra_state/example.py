"""
You would like to define a generator function, but it involves extra
state that you would like to expose to the user somehow.
"""

from collections import deque
from pathlib import Path


class LineHistory:
    def __init__(self, lines, history=3):
        self.lines = lines
        self.history = deque(maxlen=history)

    def __iter__(self):
        for i, line in enumerate(self.lines, 1):
            self.history.append((i, line))
            yield line

    def clear(self):
        self.history.clear()


def main():
    with open(Path(__file__).parent / "somefile.txt", "r") as f:
        lines = LineHistory(f)
        for line in lines:
            if "python" in line:
                print(
                    f'found python in line "{line}" - here is the current history state.'
                )
                for line_num, history_line in lines.history:
                    print(f"{line_num}:{history_line}", end="")


if __name__ == "__main__":
    main()
