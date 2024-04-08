from pydantic import BaseModel


class Clouds(BaseModel):
    all: int
    """Cloudiness as a percentage"""
