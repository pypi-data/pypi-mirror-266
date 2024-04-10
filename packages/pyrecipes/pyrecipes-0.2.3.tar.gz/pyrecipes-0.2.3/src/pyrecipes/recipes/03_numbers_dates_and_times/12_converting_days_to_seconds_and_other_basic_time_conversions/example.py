"""
You have code that needs to perform simple time conversions, like
days to seconds, hours to minutes, and so on.
"""
from datetime import timedelta, datetime


def main():
    a = timedelta(days=2, hours=6)
    b = timedelta(hours=4.5)
    c = a + b
    print("a:", a)
    print("b:", b)
    print("c:", c)
    print("c days:", c.days)
    print("seconds:", c.seconds)
    print("total seconds:", c.total_seconds())
    print("hours:", c.total_seconds() / 3600)
    print()

    d = datetime(2023, 1, 1)
    now = datetime.now()
    print("d:", d)
    print("d + a:", d + a)
    print("now:", now)
    print("now + a:", now + a)


if __name__ == "__main__":
    main()
