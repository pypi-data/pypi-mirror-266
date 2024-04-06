import asyncio
import aiohttp
from telnetapiconnector.endpoints import ConMethods
from telnetapiconnector.models import DefaultResponse
from telnetapiconnector.models import Models


endpoints = ConMethods


async def _query(url: str, params: dict, auth: aiohttp.BasicAuth) -> DefaultResponse:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url,
                               params=params,
                               auth=auth) as resp:
            return DefaultResponse(**(await resp.json()))


def _make_url_string(url: str, endp: ConMethods, ip: str):
    return url + '/' + endpoints.path + '/' + endp + '/' + ip


def get_params(port: str | None = None, model: Models | None = None) -> dict:
    params = None
    if port:
        params = {'port': port}
    if model:
        params.update({'model': model})
    return params


class Manager:
    def __init__(self, url: str, username: str, password: str):
        self._url = url
        self.auth = aiohttp.BasicAuth(username, password)

    async def get_commutator_info(self, ip: str, model: Models | None = None) -> DefaultResponse:
        params = get_params(model=model)
        url = _make_url_string(self._url, endpoints.get_comm_info, ip)
        return await _query(url, params, self.auth)

    async def get_cable_diagnostic(self, ip: str, port: str, model: Models | None = None) -> DefaultResponse:
        params = get_params(model=model, port=port)
        url = _make_url_string(self._url, endpoints.get_cab_diagnostic, ip)
        return await _query(url, params, self.auth)

    async def get_port_errors(self, ip: str, port: str, model: Models | None = None) -> DefaultResponse:
        params = get_params(port=port, model=model)
        url = _make_url_string(self._url, endpoints.get_port_errors, ip)
        return await _query(url, params, self.auth)

    async def get_port_info(self, ip: str, port: str, model: Models | None = None) -> DefaultResponse:
        params = get_params(port=port, model=model)
        url = _make_url_string(self._url, endpoints.get_port_info, ip)
        return await _query(url, params, self.auth)

    async def get_ports_count(self, ip: str, model: Models | None = None) -> DefaultResponse:
        params = get_params(model=model)
        url = _make_url_string(self._url, endpoints.get_ports_count, ip)
        return await _query(url, params, self.auth)

    async def clear_port_errors(self, ip: str, port: str, model: Models | None = None) -> DefaultResponse:
        params = get_params(port=port, model=model)
        url = _make_url_string(self._url, endpoints.clear_port_errors, ip)
        return await _query(url, params, self.auth)

