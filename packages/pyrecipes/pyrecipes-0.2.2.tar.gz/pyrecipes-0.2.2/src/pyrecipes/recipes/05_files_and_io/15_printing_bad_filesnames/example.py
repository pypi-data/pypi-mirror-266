"""
Your program received a directory listing, but when it tried to print
the filenames, it crashed with a UnicodeEncodeError exception and a
cryptic message about "surrogates not allowed".
"""


def bad_filename(filename):
    return repr(filename[1:-1])


def main():
    filename = b"\udce4d.txt"
    try:
        print(filename)
    except UnicodeEncodeError:
        print("caught bad filename")
        print(bad_filename(filename))


if __name__ == "__main__":
    main()
