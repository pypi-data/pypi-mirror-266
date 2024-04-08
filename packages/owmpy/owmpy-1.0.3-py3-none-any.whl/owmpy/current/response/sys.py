from pydantic import BaseModel


class Sys(BaseModel):
    message: str | None = None
    """System parameter, do not use it"""
    country: str | None = None
    """Country code (GB, JP etc.)"""
    sunrise: int
    """Sunrise time"""
    sunset: int
    """Sunset time"""
    type: str | None = None
    id: str | None = None
