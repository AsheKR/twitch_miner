from typing import Optional

from model.base import ConfiguredBaseModel


class Cookie(ConfiguredBaseModel):
    domain: str
    expiration_date: Optional[float]
    host_only: bool
    http_only: bool
    name: str
    path: str
    same_site: str
    secure: bool
    session: bool
    store_id: str
    value: str
