import enum
from typing import Literal

from pydantic import BaseModel
from pydantic import Field
from pydantic import HttpUrl


class DynDNSProvider(str, enum.Enum):
    ALL_INKL = enum.auto()


class AllInklProvider(BaseModel):
    provider_type: Literal[DynDNSProvider.ALL_INKL] = DynDNSProvider.ALL_INKL
    update_url: HttpUrl = Field(default=HttpUrl("https://dyndns.kasserver.com/"))
    credentials: list[tuple[str, str]]
