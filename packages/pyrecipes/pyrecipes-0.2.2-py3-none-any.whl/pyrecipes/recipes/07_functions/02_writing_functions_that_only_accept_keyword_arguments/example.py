"""
You want a function to only accept certain arguments by keyword.
"""


def recv(maxsize, *, block):
    """Receives message"""
    print(f"maxsize: {maxsize}, block: {block}")


def minimum(*values, clip=None):
    m = min(values)
    if clip is not None:
        return max(clip, m)
    return m


def example_1():
    try:
        # This fails - TtypeError
        recv(1024, True)
    except TypeError:
        recv(1024, block=True)
    print("=" * 20)


def example_2():
    a = [1, 5, 2, -5, 10]

    print("a:", a)
    print("minimum (no clip):", minimum(*a))
    print("minimum (clip=0):", minimum(*a, clip=0))


def main():
    example_1()
    example_2()


if __name__ == "__main__":
    main()
