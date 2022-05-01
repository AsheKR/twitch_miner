from model.base import ConfiguredBaseModel
from pydantic import Field


class Integrity(ConfiguredBaseModel):
    token: str
    expiration: int
    request_id: str = Field(alias="request_id")
