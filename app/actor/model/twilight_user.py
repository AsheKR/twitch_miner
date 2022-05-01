from model.base import ConfiguredBaseModel


class Role(ConfiguredBaseModel):
    is_staff: bool


class TwilightUser(ConfiguredBaseModel):
    id: str
    auth_token: str
    display_name: str
    login: str
    version: int
