from typing import NamedTuple

from .short_long import ShortLong


class Units(NamedTuple):
    temp: ShortLong = ShortLong("K", "Kelvin")
    speed: ShortLong = ShortLong("m/s", "meter/sec")
    api_name: str = "standard"

    time: tuple[str, str] = ("unix", "UTC")
    pressure: str = "hPa"
    cloudiness: str = "%"
    precipitation: ShortLong = ShortLong("mm", "millimeters")
    degrees: ShortLong = ShortLong("°", "degrees (meteorological)")
