from pydantic import BaseModel


class Rain(BaseModel):
    _1h: int | float
    _3h: int | float
