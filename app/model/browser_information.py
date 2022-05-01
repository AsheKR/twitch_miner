from pydantic import BaseModel


class UserAgentBrand(BaseModel):
    brand: str
    version: str


class UserAgentData(BaseModel):
    brands: UserAgentBrand
    mobile: bool
    platform: str


class BrowserInformation(BaseModel):
    user_agent: str
    brands: str
