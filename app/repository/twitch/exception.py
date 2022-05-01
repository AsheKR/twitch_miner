from typing import List

import requests
from model.cookie import Cookie
from repository.twitch.response.base import Error
from seleniumwire.request import Request as SeleniumWireRequest


class TwitchGQLRequestException(Exception):
    pass


class TwitchGQLResponseException(Exception):
    def __init__(self, response: requests.Response):
        self._response = response


class TwitchGQLResponseParsingException(Exception):
    def __init__(self, response: requests.Response):
        self._response = response

    def get_error(self) -> Error:
        return Error.parse_obj(self._response.json())


class TwitchGQLIntegrityTimeoutException(Exception):
    def __init__(self, cookies: List[Cookie]):
        self._cookies = cookies


class TwitchGQLIntegrityParsingException(Exception):
    def __init__(self, request: SeleniumWireRequest):
        self._request = request


class SpadeUrlParsingException(Exception):
    pass


class StreamerDoesNotExistException(Exception):
    pass


class StreamerIsOfflineException(Exception):
    pass
