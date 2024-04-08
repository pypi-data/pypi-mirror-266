"""
You have some code that needs to loop over each date in the current
month and want an efficient way to calculate that date range.
"""
from datetime import datetime, date, timedelta
import calendar


def get_month_range(start_date=None):
    if start_date is None:
        start_date = date.today().replace(day=1)
    _, days_in_month = calendar.monthrange(start_date.year, start_date.month)
    end_date = start_date + timedelta(days=days_in_month)
    return start_date, end_date


def date_range(start, stop, step):
    while start < stop:
        yield start
        start += step


def main():
    a_day = timedelta(days=1)
    first_day, last_day = get_month_range()

    while first_day < last_day:
        print(first_day)
        first_day += a_day

    print()
    for d in date_range(datetime(2023, 1, 1), datetime(2023, 1, 5), timedelta(hours=6)):
        print(d)


if __name__ == "__main__":
    main()
