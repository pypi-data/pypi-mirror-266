"""
Your application receives temporal data in string format, but you
want to convert those strings into datetime objects to perform
non-string operations on them.
"""
from datetime import datetime


def main():
    text = "2012-09-20"
    y = datetime.strptime(text, "%Y-%m-%d")
    z = datetime.now()
    print("text:", text)
    print("y:", y)
    print("now:", z)
    print("now (text):", z.strftime("%A %B %d, %Y"))
    print("now - y:", z - y)


if __name__ == "__main__":
    main()
