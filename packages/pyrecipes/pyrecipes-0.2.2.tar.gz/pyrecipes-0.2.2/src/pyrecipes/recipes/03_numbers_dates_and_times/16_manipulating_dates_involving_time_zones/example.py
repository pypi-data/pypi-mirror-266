"""
You have a conference call scheduled for December 21, 2024 at 9:30am
in Chicago. At what local time did you friend in Bangalore, India
have to show up to attend?
"""
import pytz
from datetime import datetime, timedelta
from pytz import timezone


def main():
    d = datetime(2024, 12, 21, 9, 30)
    central = timezone("US/Central")
    loc_d = central.localize(d)
    print("d:", d)
    print("central:", central)
    print("localized:", loc_d)

    bang_d = loc_d.astimezone(timezone("Asia/Kolkata"))
    print(bang_d)

    later = central.normalize(loc_d + timedelta(minutes=30))
    print(later)
    print(later.astimezone(timezone("Asia/Kolkata")))

    now_utc = datetime.now(tz=pytz.utc)
    print(now_utc)


if __name__ == "__main__":
    main()
