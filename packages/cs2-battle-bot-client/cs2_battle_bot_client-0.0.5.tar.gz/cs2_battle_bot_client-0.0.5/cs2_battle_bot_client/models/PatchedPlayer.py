from typing import *

from pydantic import BaseModel, Field

from .Nested import Nested


class PatchedPlayer(BaseModel):
    """
    None model

    """

    id: Optional[str] = Field(alias="id", default=None)

    created_at: Optional[str] = Field(alias="created_at", default=None)

    updated_at: Optional[str] = Field(alias="updated_at", default=None)

    discord_user: Optional[Nested] = Field(alias="discord_user", default=None)

    steam_user: Optional[Nested] = Field(alias="steam_user", default=None)
