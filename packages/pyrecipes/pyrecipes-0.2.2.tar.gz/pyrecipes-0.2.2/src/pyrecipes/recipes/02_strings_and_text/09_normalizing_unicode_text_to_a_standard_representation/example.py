"""
You're working with Unicode strings, but you need to make sure
that all of the strings have the same underlying representation.
"""
import unicodedata


def main():
    s1 = "Spicy Jalape\u00f1o"
    s2 = "Spicy Jalapen\u0303o"
    print("s1:", s1)
    print("s2:", s2)
    print("s1 == s2:", s1 == s2)
    print("len s1:", len(s1))
    print("len s2:", len(s2))
    print()

    t1 = unicodedata.normalize("NFC", s1)
    t2 = unicodedata.normalize("NFC", s2)
    print("t1:", t1)
    print("t2:", t2)
    print("t1 == t2:", t1 == t2)
    print("len t1:", len(t1))
    print("len t2:", len(t2))
    print("t1 ascii:", ascii(t1))
    print("t2 ascii:", ascii(t2))
    print()

    t3 = unicodedata.normalize("NFD", s1)
    t4 = unicodedata.normalize("NFD", s2)
    print("t3:", t3)
    print("t4:", t4)
    print("t3 == t4:", t3 == t4)
    print("len t3:", len(t3))
    print("len t4:", len(t4))
    print("t3 ascii:", ascii(t3))
    print("t4 ascii:", ascii(t4))
    print()

    s = "\ufb01"
    print("s:", s)
    print("s - NFD:", unicodedata.normalize("NFD", s))
    print("s - NFKC:", unicodedata.normalize("NFKC", s))
    print("s - NFKD:", unicodedata.normalize("NFKD", s))


if __name__ == "__main__":
    main()
