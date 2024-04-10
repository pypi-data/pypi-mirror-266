from typing import *

from pydantic import BaseModel, Field

from .Player import Player


class PatchedTeam(BaseModel):
    """
    None model

    """

    id: Optional[str] = Field(alias="id", default=None)

    players: Optional[List[Optional[Player]]] = Field(alias="players", default=None)

    name: Optional[str] = Field(alias="name", default=None)

    created_at: Optional[str] = Field(alias="created_at", default=None)

    updated_at: Optional[str] = Field(alias="updated_at", default=None)

    leader: Optional[str] = Field(alias="leader", default=None)
