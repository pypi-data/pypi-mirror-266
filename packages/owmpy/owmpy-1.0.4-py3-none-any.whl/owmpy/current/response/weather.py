from pydantic import BaseModel


class Weather(BaseModel):
    id: int
    """Weather condition id. See [here](https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2) for a full list of possibilities."""
    main: str
    """Group of weather parameters (Rain, Snow, Extreme etc.)"""
    description: str
    """Weather condition within the group"""
    icon: str
    """Weather icon id. Icon can be fetched with `http://openweathermap.org/img/wn/{icon}@2x.png`"""
