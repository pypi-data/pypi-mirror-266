"""
You need to decode a string of hexadecimal digits into a byte string
or encode a byte string as hex.
"""
import binascii
import base64


def main():
    s = b"hello"
    h = binascii.b2a_hex(s)
    print("s:", s)
    print("h:", h)

    print(binascii.a2b_hex(h))

    h = base64.b16encode(s)
    print(h)
    print(base64.b16decode(h))


if __name__ == "__main__":
    main()
