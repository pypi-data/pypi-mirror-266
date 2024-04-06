from pydantic import BaseModel
from pydantic import Field

from .provider import AllInklProvider


class DynDNSSetup(BaseModel):
    uuid: str
    provider: AllInklProvider = Field(discriminator="provider_type")
    name: str


class Setups(BaseModel):
    setups: list[DynDNSSetup]
