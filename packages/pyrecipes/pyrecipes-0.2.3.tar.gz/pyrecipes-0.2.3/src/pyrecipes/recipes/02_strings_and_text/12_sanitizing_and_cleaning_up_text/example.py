"""
Some bored script kiddie has entered the text 'pýtĥöñ' into a form
on your web page and you'd like to clean it up somehow.
"""
import unicodedata
import sys


def main():
    s = "pýtĥöñ\fis\tawesome\r\n"
    print("s:", s)

    remap = {ord("\t"): " ", ord("\f"): " ", ord("\r"): None}
    print("remap:", remap)

    a = s.translate(remap)
    print("a:", a)

    combined_chars = dict.fromkeys(
        c for c in range(sys.maxunicode) if unicodedata.combining(chr(c))
    )
    print("combined_chars: ", str(combined_chars)[:55], "...")

    b = unicodedata.normalize("NFD", a)
    print("b:", b)
    print("b.translate:", b.translate(combined_chars))
    print("encoded ascii:", b.encode("ascii", "ignore").decode("ascii"))

    digitmap = {
        c: ord("0") + unicodedata.digit(chr(c))
        for c in range(sys.maxunicode)
        if unicodedata.category(chr(c)) == "Nd"
    }
    print("digitmap:", str(digitmap)[:56], "...")
    print("len digitmap:", len(digitmap))

    x = "\u0661\u0662\u0663"
    print("x:", x)
    print("translated:", x.translate(digitmap))


if __name__ == "__main__":
    main()
