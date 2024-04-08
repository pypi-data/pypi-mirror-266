from pydantic import BaseModel


class Coord(BaseModel):
    lat: int | float
    """City geo location, latitude"""
    lon: int | float
    """City geo location, longitude"""
