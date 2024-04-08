from typing import Any

from aiohttp import ClientSession


class BaseClient:
    _token: str
    _client_session: ClientSession

    BASE_URL: str

    def __init__(
        self, appid: str, /, client_session: ClientSession | None = None
    ) -> None:
        self._token = appid
        self._client_session = client_session or ClientSession()

    async def _request_json(self, **params) -> Any:
        params["appid"] = self._token

        async with self._client_session.get(self.BASE_URL, params=params) as req:
            json = await req.json()
        return json

    async def close(self):
        await self._client_session.close()

    async def __aenter__(self, *args):
        return self

    async def __aexit__(self, *args):
        await self.close()
        return self
