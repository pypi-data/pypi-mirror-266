from pydantic import BaseModel


class Wind(BaseModel):
    deg: int
    """Wind direction"""
    speed: float
    """Wind speed. Differs from wind gust in that it measures instantaneous velocity."""
    gust: float | None = None
    """Wind gust. Differs from wind speed in that it measures short bursts in wind."""
