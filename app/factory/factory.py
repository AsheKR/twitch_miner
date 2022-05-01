from typing import List

import random
import time

import requests
from model.cookie import Cookie
from repository.twitch import TwitchGQLRepository, TwitchIntegrityRepository, TwitchSpadeRepository
from repository.twitch.constant import CLIENT_ID
from service.twitch import TwitchService


def wait_few_seconds(*args, **kwargs):
    time.sleep(random.uniform(0.5, 1.5))


class ServiceFactory:
    @staticmethod
    def get_twitch_service(cookies: List[Cookie], twilight_user_auth_token: str) -> TwitchService:
        session = requests.Session()
        session.hooks["response"].append(wait_few_seconds)
        session.headers.update(
            {
                "Authorization": f"OAuth {twilight_user_auth_token}",
                "Client-Id": CLIENT_ID,
            }
        )

        integrity_repository = TwitchIntegrityRepository(cookies)
        gql_repository = TwitchGQLRepository(session)
        spade_repository = TwitchSpadeRepository(session)

        return TwitchService(
            integrity_repository=integrity_repository,
            gql_repository=gql_repository,
            spade_repository=spade_repository,
        )
