from typing import NamedTuple


class ShortLong(NamedTuple):
    """Represents shorthand and longhand of a unit."""

    short: str
    """Shorthand form, eg '°C'"""
    long: str
    """Longhandform, eg 'Celsius'"""
