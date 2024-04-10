from typing import *

from pydantic import BaseModel, Field


class PatchedSteamUser(BaseModel):
    """
    None model

    """

    id: Optional[str] = Field(alias="id", default=None)

    username: Optional[str] = Field(alias="username", default=None)

    steamid64: Optional[str] = Field(alias="steamid64", default=None)

    steamid32: Optional[str] = Field(alias="steamid32", default=None)

    profile_url: Optional[str] = Field(alias="profile_url", default=None)

    avatar: Optional[str] = Field(alias="avatar", default=None)

    created_at: Optional[str] = Field(alias="created_at", default=None)

    updated_at: Optional[str] = Field(alias="updated_at", default=None)
