"""
You need to decode or encode binary data using Base64 encoding
"""
import base64


def main():
    s = b"hello"
    a = base64.b64encode(s)
    print("s:", s)
    print("a:", a)

    print("decoded:", base64.b64decode(a))


if __name__ == "__main__":
    main()
