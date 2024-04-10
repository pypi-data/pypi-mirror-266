"""
You have a byte string and you need to unpack it into an integer value.
Alternatively, you need to convert a large integer back to a byte string.
"""


def example_1():
    data = b"\x00\x124V\x00x\x90\xab\x00\xcd\xef\x01\x00#\x004"
    print("data:", data)
    print("data as int (little):", int.from_bytes(data, "little"))
    print("data as int (big):   ", int.from_bytes(data, "big"))
    print("=" * 20)


def example_2():
    number = 94522842520747284487117727783387188
    print("number:", number)
    print("number as bytes (little):", number.to_bytes(16, "little"))
    print("number as bytes (big):", number.to_bytes(16, "big"))


def main():
    example_1()
    example_2()


if __name__ == "__main__":
    main()
