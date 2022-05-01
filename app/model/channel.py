from pydantic import BaseModel


class Channel(BaseModel):
    id: str
    broadcaster_language: str
    broadcaster_login: str
    display_name: str
    thumbnail_url: str
