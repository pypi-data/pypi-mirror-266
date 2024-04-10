"""
You have a program that performs a lot of CPU-intensive work
and you would like to make it run faster by having it take
advantage of multiple CPUs.
"""

import gzip
import io
import time
from pathlib import Path
from concurrent import futures


def find_robots(filename):
    """Find all of the hosts that access robots.txt in a single log file."""
    robots = set()
    with gzip.open(filename) as f:
        for line in io.TextIOWrapper(f, encoding="ascii"):
            fields = line.split()
            if fields[6] == "/robots.txt":
                robots.add(fields[0])
    return robots


def find_all_robots(logdir):
    """Find all hosts across the entire sequence of files."""
    files = Path(logdir).glob("./*log.gz")
    all_robots = set()
    for robots in map(find_robots, files):
        all_robots.update(robots)
    return all_robots


def find_all_robots_parallel(logdir):
    """Find all hosts across the entire sequence of files."""
    files = Path(logdir).glob("./*log.gz")
    all_robots = set()
    with futures.ProcessPoolExecutor() as pool:
        for robots in pool.map(find_robots, files):
            all_robots.update(robots)
    return all_robots


def example_1():
    start = time.time()
    robots = find_all_robots(Path(__file__).parent / "logs")
    for ipaddr in robots:
        print(ipaddr)
    print(f"Took {time.time() - start}")


def example_2():
    start = time.time()
    robots = find_all_robots_parallel(Path(__file__).parent / "logs")
    for ipaddr in robots:
        print(ipaddr)
    print(f"Took {time.time() - start}")


def main():
    example_1()
    print()
    example_2()


if __name__ == "__main__":
    main()
