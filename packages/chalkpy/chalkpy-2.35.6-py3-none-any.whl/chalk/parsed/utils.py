from datetime import timedelta
from typing import Union

from chalk.utils.duration import parse_chalk_duration

# These are the maximum values that can be represented by a Duration proto.
MAX_DURATION_SECONDS = 315576000000
MAX_DURATION_NANOS = 999999999


def convert_raw_duration(duration: Union[str, timedelta]) -> timedelta:
    if isinstance(duration, str):
        duration = parse_chalk_duration(duration)
    return duration
