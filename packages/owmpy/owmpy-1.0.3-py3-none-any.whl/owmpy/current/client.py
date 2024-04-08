from typing import Any

from ..core import APIException, BaseClient
from ..utils import StandardUnits, Units
from .response import *


class Client(BaseClient):
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    async def get(
        self,
        coords: tuple[int | float, int | float],
        units: Units = StandardUnits.STANDARD,
        lang: str | None = None,
    ) -> Response:
        params = {"lat": coords[0], "lon": coords[1], "units": units.api_name}
        if lang:
            params["lang"] = lang

        json: dict[str, Any] = await self._request_json(**params)

        if "cod" in json and "message" in json:
            raise APIException(json["cod"], json["message"])
        if "rain" in json:
            keys: set[str] = set(json["rain"])
            for key in keys:
                json["rain"][f"_{key}"] = json["rain"][key]
                del json["rain"][key]

        return Response(**json, units=units)
