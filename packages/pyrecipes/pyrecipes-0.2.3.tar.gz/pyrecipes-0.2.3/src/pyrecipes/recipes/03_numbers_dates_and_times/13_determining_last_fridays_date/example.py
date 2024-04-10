"""
You want a general solution for finding a date for the last
occurance of a day of the week. Last Friday, for example.
"""
from datetime import datetime, timedelta


weekdays = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def get_previous_byday(dayname, start_date=None):
    if start_date is None:
        start_date = datetime.today()
    day_num = start_date.weekday()
    day_num_target = weekdays.index(dayname)
    days_ago = (7 + day_num - day_num_target) % 7
    if days_ago == 0:
        days_ago = 7
    return start_date - timedelta(days=days_ago)


def main():
    today = datetime.today()
    print("today:", today)
    print("last Friday:", get_previous_byday("Friday", today))
    print("last Monday:", get_previous_byday("Monday", today))
    print("last Tuesday:", get_previous_byday("Tuesday", today))

    date = datetime(2023, 6, 1, 12)
    print("date:", date)
    print("previous Friday:", get_previous_byday("Friday", date))
    print("previous Monday:", get_previous_byday("Monday", date))
    print("previous Tuesday:", get_previous_byday("Tuesday", date))


if __name__ == "__main__":
    main()
