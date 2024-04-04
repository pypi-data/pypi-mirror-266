from datetime import date, datetime

from .time import at_midnight, date_after


def test_at_midnight():
    assert at_midnight(date(1989, 2, 2)) == datetime(1989, 2, 2, 0, 0, 0)


def test_date_after():
    day = date(1999, 12, 31)
    assert date_after(day, 3) == date(2000, 1, 3)
