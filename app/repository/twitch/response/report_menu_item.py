from typing import Optional

from model.base import ConfiguredBaseModel

from .base import Extensions


class RequestInfo(ConfiguredBaseModel):
    countryCode: str
    __typename: str = "RequestInfo"


class Stream(ConfiguredBaseModel):
    id: str
    created_at: str
    __typename: str = "Stream"


class User(ConfiguredBaseModel):
    id: str
    stream: Optional[Stream]
    __typename: str = "User"


class Data(ConfiguredBaseModel):
    request_info: RequestInfo
    user: Optional[User]


class ReportMenuItem(ConfiguredBaseModel):
    data: Data
    extensions: Extensions
