"""
You're trying to match a block of text using a regular expression,
but you need the match to span multiple lines.
"""

import re


def main():
    comment = re.compile(r"/\*(.*?)\*/")
    text1 = "/* This is a comment */"
    text2 = """/* This is a\nmultiline comment */"""
    match1 = comment.findall(text1)
    match2 = comment.findall(text2)

    print("pattern:", comment)
    print("text1:", text1)
    print("text2:", text2)
    print("match1:", match1)
    print("match2:", match2)
    print()

    comment = re.compile(r"/\*((?:.|\n)*?)\*/")
    text1 = "/* This is a comment */"
    text2 = """/* This is a\nmultiline comment */"""
    match1 = comment.findall(text1)
    match2 = comment.findall(text2)

    print("pattern:", comment)
    print("text1:", text1)
    print("text2:", text2)
    print("match1:", match1)
    print("match2:", match2)


if __name__ == "__main__":
    main()
