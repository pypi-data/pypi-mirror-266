from typing import *

from pydantic import BaseModel, Field


class PatchedGuild(BaseModel):
    """
    None model

    """

    id: Optional[str] = Field(alias="id", default=None)

    name: Optional[str] = Field(alias="name", default=None)

    guild_id: Optional[str] = Field(alias="guild_id", default=None)

    lobby_channel: Optional[str] = Field(alias="lobby_channel", default=None)

    team1_channel: Optional[str] = Field(alias="team1_channel", default=None)

    team2_channel: Optional[str] = Field(alias="team2_channel", default=None)

    created_at: Optional[str] = Field(alias="created_at", default=None)

    updated_at: Optional[str] = Field(alias="updated_at", default=None)

    owner: Optional[int] = Field(alias="owner", default=None)

    members: Optional[List[str]] = Field(alias="members", default=None)
