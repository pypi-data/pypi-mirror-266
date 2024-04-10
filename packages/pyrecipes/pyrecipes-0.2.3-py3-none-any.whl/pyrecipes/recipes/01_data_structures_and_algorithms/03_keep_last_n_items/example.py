"""
You want to keep limited history of the last few items seen during iteration
or during some kind of processing.
"""

from collections import deque
from pathlib import Path


def search(lines, pattern, history=5):
    previous_lines = deque(maxlen=history)
    for line in lines:
        if pattern in line:
            yield line, previous_lines
        previous_lines.append(line)


def main():
    with open(Path(__file__).parent / "somefile.txt", "r") as f:
        for line, previous_lines in search(f, "python", 5):
            for prev_line in previous_lines:
                print(prev_line, end="")
            print(line, end="")
            print("-" * 20)


if __name__ == "__main__":
    main()
