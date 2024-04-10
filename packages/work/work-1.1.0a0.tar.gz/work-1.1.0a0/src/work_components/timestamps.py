""" API wrapper and extension for datetime """

import datetime as dt
from typing import Set


def date_equals(left: dt.date, right: dt.date) -> bool:
    """Compare date equality of arbitrary date or datetime instances.
    Handles comparison of datetime to date."""
    # Intersection is not empty => (at least) one associated date overlaps
    return bool(shared_dates(left, right))


def shared_dates(left: dt.date, right: dt.date) -> Set[dt.date]:
    """Return the date that is shared by both date or datetime instances."""
    if not isinstance(left, dt.date) or not isinstance(right, dt.date):
        raise TypeError("Expected instance of (subclass of) datetime.date.")

    left_dates = _associated_dates(left)
    right_dates = _associated_dates(right)

    return left_dates.intersection(right_dates)


def single_shared_date(left: dt.date, right: dt.date) -> dt.date:
    """Return exactly one shared date. Raises if more or less dates are shared."""
    shared = shared_dates(left, right)
    if len(shared) != 1:
        raise ValueError(f"More than one date shared between {left} and {right}.")
    return shared.pop()


def _associated_dates(given: dt.date) -> Set[dt.date]:
    """
    Return the associated date(s) of the given date or datetime.

    - For a date, return {date}.
    - For a datetime with time != 0:00, return {day}
    - For a datetime with time == 0:00, return {day before, day}
    """
    if not isinstance(given, dt.datetime):
        assert isinstance(given, dt.date)
        return {given}
    if given.time() != dt.time(0, 0):
        return {given.date()}
    return {given.date() - dt.timedelta(days=1), given.date()}
