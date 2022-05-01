from typing import Dict, List, Type, Union, cast

import copy
import json
import re
from base64 import b64encode

import requests
import seleniumwire.undetected_chromedriver as uc
from model.cookie import Cookie
from pydantic import BaseModel, ValidationError
from pyvirtualdisplay import Display
from selenium.common import TimeoutException

from .constant import TWITCH_GQL_URL, TWITCH_URL, GQLOperations
from .exception import (
    SpadeUrlParsingException,
    TwitchGQLIntegrityParsingException,
    TwitchGQLIntegrityTimeoutException,
    TwitchGQLRequestException,
    TwitchGQLResponseException,
    TwitchGQLResponseParsingException,
)
from .response import ReportMenuItem
from .response.channel_points_context import ChannelPointsContext
from .response.claim_community_points import ClaimCommunityPoints
from .response.integrity import Integrity
from .response.video_player_stream_info_overlay_channel import VideoPlayerStreamInfoOverlayChannel


class TwitchSpadeRepository:
    def __init__(self, session: requests.Session):
        self._session = session

    @staticmethod
    def get_spade_url(broadcaster_login: str) -> str:
        try:
            main_page_request = requests.get(f"{TWITCH_URL}/{broadcaster_login}")
            response = main_page_request.text
            regex_settings = "(https://static.twitchcdn.net/config/settings.*?js)"
            settings_url = re.search(regex_settings, response).group(1)

            settings_request = requests.get(settings_url)
            response = settings_request.text
            regex_spade = '"spade_url":"(.*?)"'
            return re.search(regex_spade, response).group(1)
        except Exception as e:
            raise SpadeUrlParsingException from e

    @staticmethod
    def get_minute_watched_payload(channel_id: str, stream_id: str, twilight_user_id: str) -> dict:
        payload = [
            {
                "event": "minute-watched",
                "properties": {
                    "channel_id": channel_id,
                    "broadcast_id": stream_id,
                    "player": "site",
                    "user_id": twilight_user_id,
                },
            }
        ]
        json_event = json.dumps(payload, separators=(",", ":"))
        return {"data": (b64encode(json_event.encode("utf-8"))).decode("utf-8")}

    def minute_watched(self, spade_url: str, encoded_payload: dict) -> None:
        self._session.post(spade_url, data=encoded_payload)


class TwitchIntegrityRepository:
    def __init__(self, cookies: List[Cookie]):
        self._cookies = cookies

    def get_integrity(self) -> Integrity:
        with Display():
            with uc.Chrome() as driver:
                driver.get(TWITCH_URL)

                for cookie in self._cookies:
                    if cookie.domain == ".twitch.tv":
                        driver.add_cookie(cookie.dict(by_alias=True, include={"name", "value", "domain"}))

                driver.backend.storage.clear_requests()
                driver.get(TWITCH_URL)

                try:
                    request = driver.wait_for_request("https://gql.twitch.tv/integrity", timeout=20)
                    try:
                        body = request.response.body.decode("UTF-8")
                        integrity = Integrity.parse_obj(json.loads(body))
                        return integrity
                    except Exception as e:
                        raise TwitchGQLIntegrityParsingException(request) from e
                except TimeoutException:
                    raise TwitchGQLIntegrityTimeoutException(cookies=self._cookies)
                except TwitchGQLIntegrityParsingException as e:
                    raise e


class TwitchGQLRepository:
    def __init__(self, session: requests.Session):
        self._session = session

    def request(
        self, json_data: dict, klass: Type[BaseModel] = None, additional_headers: Dict[str, str] = None
    ) -> Union[BaseModel, dict]:
        try:
            response = self._session.post(
                TWITCH_GQL_URL,
                headers={
                    **self._session.headers,
                    **(additional_headers or {}),
                },
                json=json_data,
            )

            if response.status_code // 100 != 2:
                raise TwitchGQLResponseException(response)

            response_data = response.json()

            if klass:
                try:
                    return klass.parse_obj(response_data)
                except ValidationError as e:
                    raise TwitchGQLResponseParsingException(response) from e

            return response_data
        except TwitchGQLResponseParsingException as e:
            raise e
        except Exception as e:
            raise TwitchGQLRequestException from e

    def get_channel_info(self, broadcaster_login: str) -> ReportMenuItem:
        json_data = copy.deepcopy(GQLOperations.ReportMenuItem)
        json_data["variables"] = {"channelLogin": broadcaster_login}
        return cast(ReportMenuItem, self.request(json_data, ReportMenuItem))

    def get_stream_info(self, broadcaster_login: str) -> VideoPlayerStreamInfoOverlayChannel:
        json_data = copy.deepcopy(GQLOperations.VideoPlayerStreamInfoOverlayChannel)
        json_data["variables"] = {"channel": broadcaster_login}
        return cast(VideoPlayerStreamInfoOverlayChannel, self.request(json_data, VideoPlayerStreamInfoOverlayChannel))

    def get_channel_points_context(self, broadcaster_login: str) -> ChannelPointsContext:
        json_data = copy.deepcopy(GQLOperations.ChannelPointsContext)
        json_data["variables"] = {"channelLogin": broadcaster_login}

        return cast(ChannelPointsContext, self.request(json_data, ChannelPointsContext))

    def claim_bonus(self, channel_id: str, claim_id: str, integrity_token: str, device_id: str) -> ClaimCommunityPoints:
        json_data = copy.deepcopy(GQLOperations.ClaimCommunityPoints)
        json_data["variables"] = {"input": {"channelID": channel_id, "claimID": claim_id}}
        return cast(
            ClaimCommunityPoints,
            self.request(
                json_data,
                ClaimCommunityPoints,
                additional_headers={
                    "Client-Integrity": integrity_token,
                    "X-Device-Id": device_id,
                },
            ),
        )
