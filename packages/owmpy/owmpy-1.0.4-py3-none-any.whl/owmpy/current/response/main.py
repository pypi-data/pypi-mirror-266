from pydantic import BaseModel


class Main(BaseModel):
    temp: float
    """Temperature"""
    humidity: int | float
    """Humidity"""
    feels_like: int | float
    """Temperature (felt)"""
    temp_min: int | float
    """Minimum temperature at the moment. This is deviation from current temp that is possible for large cities and megalopolises geographically expanded (use these parameters optionally)"""
    temp_max: float
    """Maximum temperature at the moment. This is deviation from current temp that is possible for large cities and megalopolises geographically expanded (use these parameters optionally)"""
    pressure: int
    """Atmospheric pressure (on the sea level, if there is no sea_level or grnd_level data)"""
    sea_level: int | None = None
    """Atmospheric pressure on the sea level"""
    grnd_level: int | None = None
    """Atmospheric pressure on the ground level"""
