from model.base import ConfiguredBaseModel


class ChannelInfo(ConfiguredBaseModel):
    channel_id: str
    spade_url: str
    is_online: bool
