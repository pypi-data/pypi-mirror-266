from typing import *

from pydantic import BaseModel, Field

from .Player import Player


class Team(BaseModel):
    """
    None model

    """

    id: str = Field(alias="id")

    players: List[Player] = Field(alias="players")

    name: str = Field(alias="name")

    created_at: str = Field(alias="created_at")

    updated_at: str = Field(alias="updated_at")

    leader: Optional[str] = Field(alias="leader", default=None)
