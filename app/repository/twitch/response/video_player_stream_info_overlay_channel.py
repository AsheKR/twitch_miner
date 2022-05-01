from typing import List, Optional

from model.base import ConfiguredBaseModel
from pydantic import Field

from .base import Extensions


class Game(ConfiguredBaseModel):
    id: str
    displayName: str
    name: str
    __typename: str = "Game"


class BroadcastSettings(ConfiguredBaseModel):
    id: str
    title: str
    game: Game
    __typename: str = "BroadcastSettings"


class Tag(ConfiguredBaseModel):
    id: str
    localized_name: str
    __typename: str = "Tag"


class Stream(ConfiguredBaseModel):
    id: str
    viewers_count: int
    tags: List[Tag]
    __typename: str = "Stream"


class User(ConfiguredBaseModel):
    id: str
    profile_url: str = Field(alias="profileURL")
    display_name: str
    login: str
    profile_image_url: str = Field(alias="profileImageURL")
    broadcast_settings: BroadcastSettings
    stream: Optional[Stream]
    __typename: str = "User"


class Data(ConfiguredBaseModel):
    user: User


class VideoPlayerStreamInfoOverlayChannel(ConfiguredBaseModel):
    data: Data
    extensions: Extensions
