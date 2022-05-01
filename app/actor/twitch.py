from typing import Dict, List, Optional

import json
import random
import time
from urllib.parse import unquote

from actor.exception import CookieNameNotFoundException
from actor.model.channel_info import ChannelInfo
from actor.model.twilight_user import TwilightUser
from factory import ServiceFactory
from model.channel import Channel
from model.cookie import Cookie
from pydantic import parse_obj_as
from repository import ChallengeType
from service import ClaimBonusException
from structlog import get_logger

logger = get_logger()


def get_value_from_cookies(name: str, cookies: List[Cookie]) -> Optional[str]:
    try:
        return next(cookie.value for cookie in cookies if cookie.name == name)
    except StopIteration:
        raise CookieNameNotFoundException(name)


def get_twilight_user(raw_twilight_user: str) -> TwilightUser:
    twilight_user_parsed_data: str = unquote(str(raw_twilight_user))
    return TwilightUser.parse_obj(json.loads(twilight_user_parsed_data))


def mine(raw_channels: str, raw_cookies: str):
    channels: List[Channel] = parse_obj_as(List[Channel], json.loads(raw_channels))
    cookies: List[Cookie] = parse_obj_as(List[Cookie], json.loads(raw_cookies))

    device_id = get_value_from_cookies("unique_id", cookies)
    raw_twilight_user = get_value_from_cookies("twilight-user", cookies)
    twilight_user = get_twilight_user(raw_twilight_user)

    twitch_service = ServiceFactory.get_twitch_service(cookies, twilight_user.auth_token)

    integrity_token = twitch_service.get_integrity_token()

    channel_infos: Dict[str, ChannelInfo] = {}
    for channel in channels:
        spade_url = twitch_service.get_spade_url(channel.broadcaster_login)
        is_online = twitch_service.is_channel_online(channel.broadcaster_login)
        logger.info(f"[{channel.display_name}] Current Online Status: {is_online}")
        channel_infos[channel.id] = ChannelInfo.parse_obj(
            {
                "channelId": channel.id,
                "spadeUrl": spade_url,
                "isOnline": is_online,
            }
        )

    while True:
        for index, channel in enumerate(channels):
            is_online = twitch_service.is_channel_online(channel.broadcaster_login)

            if channel_infos[channel.id].is_online != is_online:
                logger.info(
                    f"[{channel.display_name}] Change Online Status: {channel_infos[channel.id].is_online} -> {is_online}"
                )
                channel_infos[channel.id].is_online = is_online

            if is_online:
                current_point = twitch_service.get_current_point(channel.broadcaster_login)
                logger.info(f"[{channel.display_name}] Current Point: {current_point}")

                stream_id = twitch_service.get_stream_id(channel.broadcaster_login)

                payload = twitch_service.get_watch_bonus_payload(
                    channel.id, stream_id, twilight_user_id=twilight_user.id
                )
                twitch_service.gain_watch_bonus(channel_infos[channel.id].spade_url, payload)
                time.sleep(random.uniform(5, 6))

                after_watch_point = twitch_service.get_current_point(channel.broadcaster_login)
                logger.info(f"[{channel.display_name}] After Watch Point: {after_watch_point}")

                if current_point != after_watch_point:
                    logger.info(f"[{channel.display_name}] Gain Minute Bonus: + {after_watch_point - current_point}")

                if twitch_service.is_available_claim_bonus(channel.broadcaster_login):
                    claim_id = twitch_service.get_claim_id(channel.broadcaster_login)
                    try:
                        bonus_point = twitch_service.claim_bonus(channel.id, claim_id, integrity_token, device_id)
                        logger.info(f"[{channel.display_name}] Gain Click Bonus: + {bonus_point}")
                    except ClaimBonusException as e:
                        error = e.get_error()
                        if error.extensions.challenge.type == ChallengeType.INTEGRITY:
                            integrity_token = twitch_service.get_integrity_token()

        time.sleep(random.uniform(120, 180))
