from typing import *

from pydantic import BaseModel, Field


class Guild(BaseModel):
    """
    None model

    """

    id: str = Field(alias="id")

    name: str = Field(alias="name")

    guild_id: str = Field(alias="guild_id")

    lobby_channel: Optional[str] = Field(alias="lobby_channel", default=None)

    team1_channel: Optional[str] = Field(alias="team1_channel", default=None)

    team2_channel: Optional[str] = Field(alias="team2_channel", default=None)

    created_at: str = Field(alias="created_at")

    updated_at: str = Field(alias="updated_at")

    owner: int = Field(alias="owner")

    members: List[str] = Field(alias="members")
