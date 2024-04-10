"""
You have long strings that you want to reformat so that they fill a
user-specified number of columns.
"""
import textwrap
import os


def main():
    s = (
        "Look into my eyes, look into my eyes, the eyes, the eyes, "
        "the eyes, not around the eyes, don't look around the eyes, "
        "you're under"
    )
    print(s)

    print(textwrap.fill(s, 70))
    print(textwrap.fill(s, 40))
    print(textwrap.fill(s, 40, initial_indent="    "))
    print(textwrap.fill(s, 40, subsequent_indent="    "))

    try:
        columns = os.get_terminal_size().columns
        print("terminal size:", columns)
    except OSError:
        print("no terminal")


if __name__ == "__main__":
    main()
