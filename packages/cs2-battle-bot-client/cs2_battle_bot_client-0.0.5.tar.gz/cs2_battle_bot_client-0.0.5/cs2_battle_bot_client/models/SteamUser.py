from typing import *

from pydantic import BaseModel, Field


class SteamUser(BaseModel):
    """
    None model

    """

    id: str = Field(alias="id")

    username: str = Field(alias="username")

    steamid64: Optional[str] = Field(alias="steamid64", default=None)

    steamid32: Optional[str] = Field(alias="steamid32", default=None)

    profile_url: Optional[str] = Field(alias="profile_url", default=None)

    avatar: Optional[str] = Field(alias="avatar", default=None)

    created_at: str = Field(alias="created_at")

    updated_at: str = Field(alias="updated_at")
