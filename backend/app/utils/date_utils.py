"""
Working-day calculation utilities.

Business rule: Saturdays, Sundays, and active company holidays are excluded
from leave-day counts. Half-day leave is not supported - every valid day
counts as exactly one full day.
"""
from datetime import date, timedelta

SATURDAY = 5
SUNDAY = 6


def count_working_days(start_date: date, end_date: date, holiday_dates: set[date]) -> int:
    """
    Count the number of valid working days (inclusive of both start_date and
    end_date) between two dates, excluding weekends and holidays.
    """
    if end_date < start_date:
        return 0

    working_days = 0
    current = start_date
    while current <= end_date:
        if current.weekday() not in (SATURDAY, SUNDAY) and current not in holiday_dates:
            working_days += 1
        current += timedelta(days=1)
    return working_days
