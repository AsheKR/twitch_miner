from pydantic import BaseModel
from util.inflection import to_camel_case


class ConfiguredBaseModel(BaseModel):
    class Config:
        alias_generator = to_camel_case
