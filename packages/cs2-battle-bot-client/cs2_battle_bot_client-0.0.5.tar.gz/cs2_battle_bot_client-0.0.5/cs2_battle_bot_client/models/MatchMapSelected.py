from typing import *

from pydantic import BaseModel, Field

from .Map import Map
from .Team import Team


class MatchMapSelected(BaseModel):
    """
    None model

    """

    id: int = Field(alias="id")

    team: Team = Field(alias="team")

    map: Map = Field(alias="map")

    created_at: str = Field(alias="created_at")

    updated_at: str = Field(alias="updated_at")
