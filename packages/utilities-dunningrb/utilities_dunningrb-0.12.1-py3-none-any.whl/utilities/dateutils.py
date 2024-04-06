"""Define utility methods for working with dates and datetime objects.
"""
from __future__ import annotations

import calendar
from datetime import datetime, timedelta

DAYS_PER_CENTURY = 36_525
JAN_1_2000_NOON = 2_451_545  # Julian day number.
SHORT_DATE_FORMAT = "%Y-%m-%d"  # ISO-8601.


def get_clock_time() -> str:
    return datetime.now().strftime("%H:%M:%S")


def check_date_format(*, date: str, dtformat: str = None) -> bool:
    """Return True if the given <<date>> is formatted according to
    <<dt_format>>, otherwise False.
    """
    dtformat = SHORT_DATE_FORMAT if dtformat is None else dtformat
    try:
        datetime.strptime(date, dtformat)
    except ValueError:
        return False
    return True


def get_date_ahead(r: datetime = datetime.now(), *, days_ahead: int) -> datetime:
    return r + timedelta(days_ahead)


def get_date_short_str(*, date: datetime) -> str:
    return date.strftime(SHORT_DATE_FORMAT)


def get_datestamp(date: datetime = None, with_time: bool = False) -> str:
    now = datetime.now() if date is None else date
    if with_time:
        datestamp = now.isoformat().split(".")[0].replace(":", "-")
    else:
        datestamp = now.isoformat().split("T")[0]
    return datestamp


def get_datetime_instance(*, date: str) -> datetime:
    """Return a datetime instance."""
    return datetime.strptime(date, SHORT_DATE_FORMAT)


def get_julian_centuries(*, date: datetime) -> float:
    """Convert the given date into the number of Julian centuries Jan 1, 2000, Noon.
    """
    julian_date = get_julian_day(date=date)
    julian_centuries = (julian_date - JAN_1_2000_NOON) / DAYS_PER_CENTURY

    return julian_centuries


def get_julian_day(*, date: datetime) -> float:
    """Convert the given date into the Julian day number.

    Note: year is restricted as follows:

        1901 <= year <= 2099
    """
    year = date.year

    if not (1901 <= year <= 2099):
        raise ValueError(
            f"The year must between 1901 and 2099, inclusive. Received: {year}."
        )

    month = date.month
    day = date.day
    hour = date.hour
    minute = date.minute
    second = date.second
    universal_time = hour + minute / 60 + second / 3600
    ut_fraction = universal_time / 24

    part_a = 367 * year
    part_b_numerator = 7 * (year + int((month + 9) / 12))
    part_b = int(part_b_numerator / 4)
    part_c = int((275 * month) / 9)

    julian_day = part_a - part_b + part_c + day + 1_721_013.5 + ut_fraction

    return julian_day


def get_last_date_of(r: datetime, *, step: str) -> datetime:
    """If step is one week, return the date for the first Sunday on or after the given date <r>.
    If step is one month, return the date for the last day of the month containing <r>.
    """
    if step.strip().lower() == "week":
        days_left = 7 - r.isoweekday()
        last_date = r + timedelta(days_left)
    elif step.strip().lower() == "month":
        last_day = calendar.monthrange(r.year, r.month)[-1]
        last_date = datetime(r.year, r.month, last_day)

    return last_date
