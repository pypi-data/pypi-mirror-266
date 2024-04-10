"""
This module contains examples of day count fraction calculations.
"""

from datetime import datetime, timedelta


def _is_eom(dt):
    return (dt + timedelta(days=1)).month != dt.month


def dcf_30_360(end: datetime, start: datetime) -> float:
    """Calculate US 30/360 daycount fraction. It is a simple
    implementation, and may not capture all the edge cases.

    Args:
        end: the end date.
        start: the start date.
    """
    if _is_eom(start):
        d1 = 30
    else:
        d1 = start.day

    if d1 == 30 and end.day == 31:
        d2 = 30
    else:
        d2 = end.day

    return (
        (end.year - start.year)
        + (end.month - start.month) / 12
        + (d2 - d1) / 360
    )
