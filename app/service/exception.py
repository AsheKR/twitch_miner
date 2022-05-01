from repository.twitch.exception import TwitchGQLResponseParsingException as RepositoryTwitchGQLResponseParsingException
from repository.twitch.response.base import Error


class ClaimBonusException(Exception):
    def __init__(self, exception: RepositoryTwitchGQLResponseParsingException):
        self._exception = exception

    def get_error(self) -> Error:
        return self._exception.get_error()
