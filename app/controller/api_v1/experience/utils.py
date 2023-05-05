import pytz
from datetime import datetime


def validate_new_slot(
    start_time,
    end_time,
    existing_slots
):
    if start_time < datetime.now(tz=pytz.utc):
        return False

    low = 0
    high = len(existing_slots) - 1

    while low <= high:
        mid = int((low + high) / 2)
        if existing_slots[mid].end_time <= start_time:
            low = mid + 1
        elif existing_slots[mid].start_time >= end_time:
            high = mid - 1
        else:
            return False

    return True
