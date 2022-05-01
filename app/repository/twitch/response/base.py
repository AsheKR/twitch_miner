from typing import List, Optional

from enum import Enum

from model.base import ConfiguredBaseModel
from pydantic import Field


class ChallengeType(Enum):
    INTEGRITY = "integrity"


class Challenge(ConfiguredBaseModel):
    type: ChallengeType


class Extensions(ConfiguredBaseModel):
    duration_milliseconds: int
    operation_name: str
    request_id: str = Field(alias="requestID")
    challenge: Optional[Challenge]


class Message(ConfiguredBaseModel):
    message: str


class Error(ConfiguredBaseModel):
    errors: List[Message]
    extensions: Extensions
