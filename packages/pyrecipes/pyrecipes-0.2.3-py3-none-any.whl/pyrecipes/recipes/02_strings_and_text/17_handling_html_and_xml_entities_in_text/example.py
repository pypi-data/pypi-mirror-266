"""
You want to replace HTML or XML entities such as &entity; or &#code;
with their corresponding text. Alternatively, you need to produce
text, but escape certain characters (e.g. <, >, &)
"""
import html
from xml.sax.saxutils import unescape


def main():
    s = 'Elements are writen as "<tag>text</tag>".'
    print(s)
    print(html.escape(s))
    print(html.escape(s, quote=False), end="\n\n")

    s = "Spicy Jalapeño"
    print(s)
    print(s.encode("ascii", errors="xmlcharrefreplace"), end="\n\n")

    s = "Spicy &quot;Jalape&#241;o&quot;"
    print(s)
    print(html.unescape(s), end="\n\n")

    t = "The prompt is &gt;&gt;&gt;"
    print(t)
    print(unescape(t))


if __name__ == "__main__":
    main()
