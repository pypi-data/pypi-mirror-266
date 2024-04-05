from datetime import date, datetime
from typing import Any


def parse_int(value: Any) -> int | None:
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def age_from(birthday: datetime | None) -> int | None:
    if not birthday or birthday == datetime.min:
        return None
    today = date.today()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
