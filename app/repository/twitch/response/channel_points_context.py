from typing import List, Optional

from model.base import ConfiguredBaseModel
from pydantic import Field

from .base import Extensions


class Multiplier(ConfiguredBaseModel):
    reasonCode: str
    factor: float
    __typename: str = "CommunityPointsMultiplier"


class WatchStreakEarningSettings(ConfiguredBaseModel):
    points: int
    __typename: str = "CommunityPointsWatchStreakEarningSettings"


class ChannelEarningSettings(ConfiguredBaseModel):
    id: str
    average_points_per_hour: int
    cheer_points: int
    claim_points: int
    follow_points: int
    passive_watch_points: int
    raid_points: int
    subscription_gift_points: int
    watch_streak_points: List[WatchStreakEarningSettings]
    multipliers: List[Multiplier]
    __typename: str = "CommunityPointsChannelEarningSettings"


class Settings(ConfiguredBaseModel):
    is_enabled: bool
    raid_point_amount: int
    earning: ChannelEarningSettings
    __typename: str = "CommunityPointsChannelSettings"


class AvailableClaim(ConfiguredBaseModel):
    id: str
    __typename: str = "CommunityPointsClaim"


class CommunityPointsProperties(ConfiguredBaseModel):
    available_claim: Optional[AvailableClaim]
    balance: int
    __typename: str = "CommunityPointsProperties"


class ChannelSelfEdge(ConfiguredBaseModel):
    community_points: CommunityPointsProperties
    __typename: str = "ChannelSelfEdge"


class Channel(ConfiguredBaseModel):
    id: str
    self: ChannelSelfEdge
    community_points_settings: Settings
    __typename: str = "Channel"


class Community(ConfiguredBaseModel):
    id: str
    display_name: str
    channel: Channel
    __typename: str = "User"


class Data(ConfiguredBaseModel):
    community: Community


class ChannelPointsContext(ConfiguredBaseModel):
    data: Data
    extensions: Extensions
