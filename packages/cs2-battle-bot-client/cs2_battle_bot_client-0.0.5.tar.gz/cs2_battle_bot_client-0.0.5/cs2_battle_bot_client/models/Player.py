from typing import *

from pydantic import BaseModel, Field

from .Nested import Nested


class Player(BaseModel):
    """
    None model

    """

    id: str = Field(alias="id")

    created_at: str = Field(alias="created_at")

    updated_at: str = Field(alias="updated_at")

    discord_user: Nested = Field(alias="discord_user")

    steam_user: Nested = Field(alias="steam_user")
