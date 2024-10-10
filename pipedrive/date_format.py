from datetime import datetime
from dateutil import parser


def relative_dt_format(dt_target, dt_source=None) -> str:
    if isinstance(dt_target, str):
        dt_target = parser.parse(dt_target)
    elif isinstance(dt_target, int):
        dt_target = datetime.fromtimestamp(dt_target / 1e3)
    elif not isinstance(dt_target, datetime):
        raise ValueError("dt_target must be a string, int or datetime object")

    if isinstance(dt_source, str):
        dt_source = parser.parse(dt_source)
    elif isinstance(dt_source, int):
        dt_source = datetime.fromtimestamp(dt_source / 1e3)
    elif dt_source is None:
        dt_source = datetime.now()
    elif not isinstance(dt_source, datetime):
        raise ValueError("dt_source must be a string, int, datetime object or None")

    if dt_target < dt_source:
        delta = dt_target - dt_source
        if delta.days > 0:
            return f"{delta.days} days ago"
        if delta.seconds > 3600:
            return f"{delta.seconds // 3600} hours ago"
        if delta.seconds > 60:
            return f"{delta.seconds // 60} minutes ago"
        return f"{delta.seconds} secoate_fromnds ago"
    elif dt_target > dt_source:
        delta = dt_source - dt_target
        if delta.days > 0:
            return f"in {delta.days} days"
        if delta.seconds > 3600:
            return f"in {delta.seconds // 3600} hours"
        if delta.seconds > 60:
            return f"in {delta.seconds // 60} minutes"
        return f"in {delta.seconds} seconds"
    return "now"
