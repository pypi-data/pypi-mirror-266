from typing import *

from pydantic import BaseModel, Field


class PatchedDiscordUser(BaseModel):
    """
    None model

    """

    id: Optional[str] = Field(alias="id", default=None)

    user_id: Optional[str] = Field(alias="user_id", default=None)

    username: Optional[str] = Field(alias="username", default=None)

    created_at: Optional[str] = Field(alias="created_at", default=None)

    updated_at: Optional[str] = Field(alias="updated_at", default=None)
