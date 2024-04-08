from pydantic import BaseModel

from ...utils import StandardUnits, Units
from .clouds import Clouds
from .coord import Coord
from .main import Main
from .rain import Rain
from .sys import Sys
from .weather import Weather
from .wind import Wind


class Response(BaseModel):
    """The weather data served by https://openweathermap.org/current. Most docstrings stolen from there too."""

    units: Units = StandardUnits.STANDARD
    """Units to use. Served by internal API."""
    id: int
    """City identification"""
    dt: int
    """Data receiving time"""
    name: str
    """City name"""
    coord: Coord
    """Geographical coordinates"""
    sys: Sys
    """Location data"""
    wind: Wind
    clouds: Clouds
    weather: list[Weather]
    """A list of weather responses. Usually one item."""
    rain: Rain | None = None
    """Rain data. May not exist."""
    base: str
    main: Main
    visibility: int
    timezone: int
    cod: int
