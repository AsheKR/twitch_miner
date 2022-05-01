from repository import (
    TwitchGQLRepository,
    TwitchGQLResponseParsingException,
    TwitchIntegrityRepository,
    TwitchSpadeRepository,
)
from service import ClaimBonusException


class TwitchService:
    def __init__(
        self,
        spade_repository: TwitchSpadeRepository,
        gql_repository: TwitchGQLRepository,
        integrity_repository: TwitchIntegrityRepository,
    ):
        self._spade_repository = spade_repository
        self._gql_repository = gql_repository
        self._integrity_repository = integrity_repository

    def get_channel_id(self, broadcaster_login: str) -> str:
        return self._gql_repository.get_channel_info(broadcaster_login).data.user.id

    def get_spade_url(self, broadcaster_login: str) -> str:
        return self._spade_repository.get_spade_url(broadcaster_login)

    def get_integrity_token(self) -> str:
        return self._integrity_repository.get_integrity().token

    def is_channel_online(self, broadcaster_login: str) -> bool:
        return bool(self._gql_repository.get_stream_info(broadcaster_login).data.user.stream)

    def get_stream_id(self, broadcaster_login: str) -> str:
        return self._gql_repository.get_stream_info(broadcaster_login).data.user.stream.id

    def get_current_point(self, broadcaster_login: str) -> int:
        return self._gql_repository.get_channel_points_context(
            broadcaster_login
        ).data.community.channel.self.community_points.balance

    def get_watch_bonus_payload(self, channel_id: str, stream_id: str, twilight_user_id) -> dict:
        # "twilight_user_id" will get from cookie data
        return self._spade_repository.get_minute_watched_payload(channel_id, stream_id, twilight_user_id)

    def gain_watch_bonus(self, spade_url: str, payload: dict) -> None:
        # The point is not applied immediately, but it is applied after a few seconds
        self._spade_repository.minute_watched(spade_url, payload)

    def is_available_claim_bonus(self, broadcaster_login: str) -> bool:
        return bool(
            self._gql_repository.get_channel_points_context(
                broadcaster_login
            ).data.community.channel.self.community_points.available_claim
        )

    def get_claim_id(self, broadcaster_login: str) -> str:
        return self._gql_repository.get_channel_points_context(
            broadcaster_login
        ).data.community.channel.self.community_points.available_claim.id

    def claim_bonus(self, channel_id: str, claim_id: str, integrity_token: str, device_id: str) -> int:
        # "device_id" will get from cookie data ( unique_id )
        # integrity token can be expired, when ClamBonusException raise, reissue integrity token
        try:
            return self._gql_repository.claim_bonus(
                channel_id, claim_id, integrity_token, device_id
            ).data.claim_community_points.claim.points_earned_total
        except TwitchGQLResponseParsingException as e:
            raise ClaimBonusException(e) from e
