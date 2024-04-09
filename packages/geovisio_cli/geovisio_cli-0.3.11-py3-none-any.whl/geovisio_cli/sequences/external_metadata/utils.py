import datetime
from typing import Optional
import re
from geovisio_cli import exception


def parse_hms(value: str, ref: int) -> Optional[float]:
    r"""Compute decimal coordinates (latitude or longitude) from degrees/minutes/seconds coordinates.

    Args:
        value: raw lat (or lon)
        ref: 1 if the value is North or East

    Returns:
        float: real lat (or lon) or None if a problem occurs
    >>> parse_hms("50° 30' 54.36\"", 1)
    50.5151
    >>> parse_hms("plop", 1) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    geovisio_cli.exception.CliException: impossible to parse position: plop
    """
    result = re.search(r"(\d+)° (\d+)' (.+?)\"", value)
    if not result:
        raise exception.CliException(f"impossible to parse position: {value}")
    h, m, s = result.groups()
    return (float(h) + float(m) / 60 + float(s) / 3600) * ref


def check_lat(value: Optional[str]) -> Optional[float]:
    """parse and check latitude"""
    if not value:
        return None
    try:
        f = float(value)
    except ValueError as e:
        raise exception.CliException(f"Impossible to parse latitude ({str(e)})")
    if f < -90 or f > 90:
        raise exception.CliException(
            f"latitude '{f}' is out of WGS84 bounds (should be in [-90, 90]"
        )
    return f


def check_lon(value: Optional[str]) -> Optional[float]:
    """parse and check longitude"""
    if not value:
        return None
    try:
        f = float(value)
    except ValueError as e:
        raise exception.CliException(f"Impossible to parse longitude ({str(e)})")
    if f < -180 or f > 180:
        raise exception.CliException(
            f"longitude '{f}' is out of WGS84 bounds (should be in [-180, 180]"
        )
    return f


def parse_capture_time(value: Optional[str]) -> Optional[float]:
    """
    Parse an RFC 3339 formated date and return the timestamp
    """
    if not value:
        return None
    try:
        d = datetime.datetime.fromisoformat(value)
    except Exception as e:
        raise exception.CliException(
            f"The capture_time was not recognized (should follow the RFC 3339): {value} ({str(e)})"
        )
    return d.timestamp()
