
import re
import datetime
from typing import Tuple

def today_str(format: str = "%Y-%m-%d") -> str:
    """Return today's date in string format."""
    return datetime.datetime.now().strftime(format)


date_str_regexp = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
def date_from_str(date_str: str) -> datetime.date:
    """Convertt '%Y-%m-%d' formatted string to datetime.date object"""
    match = date_str_regexp.match(date_str)
    if not match:
        raise ValueError(f"Invalid date string: {date_str}, expected format: %Y-%m-%d")
    year, month, day = match.groups()
    return datetime.date(int(year), int(month), int(day))


def check_from_date_and_to_date_validity(from_date_str: str, to_date_str: str) -> Tuple[datetime.date, datetime.date]:
    from_date = date_from_str(from_date_str)
    to_date = date_from_str(to_date_str)
    if from_date > to_date:
        raise ValueError(f"from_date {from_date_str} is later than {to_date_str}")
    return from_date, to_date


__all__ = [
    "today_str",
    "date_from_str",
    "check_from_date_and_to_date_validity",
]
