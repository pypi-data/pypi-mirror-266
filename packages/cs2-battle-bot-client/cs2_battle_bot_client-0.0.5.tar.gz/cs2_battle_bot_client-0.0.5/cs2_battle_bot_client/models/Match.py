from typing import *

from pydantic import BaseModel, Field

from .Map import Map
from .MapBan import MapBan
from .MatchMapSelected import MatchMapSelected
from .StatusEnum import StatusEnum
from .Team import Team
from .TypeEnum import TypeEnum


class Match(BaseModel):
    """
    None model

    """

    id: int = Field(alias="id")

    team1: Team = Field(alias="team1")

    team2: Team = Field(alias="team2")

    winner_team: Team = Field(alias="winner_team")

    maps: List[Map] = Field(alias="maps")

    map_bans: List[MapBan] = Field(alias="map_bans")

    map_picks: List[MatchMapSelected] = Field(alias="map_picks")

    connect_command: str = Field(alias="connect_command")

    load_match_command: str = Field(alias="load_match_command")

    status: Optional[StatusEnum] = Field(alias="status", default=None)

    type: Optional[TypeEnum] = Field(alias="type", default=None)

    num_maps: Optional[int] = Field(alias="num_maps", default=None)

    maplist: Optional[Any] = Field(alias="maplist", default=None)

    map_sides: Optional[Any] = Field(alias="map_sides", default=None)

    clinch_series: Optional[bool] = Field(alias="clinch_series", default=None)

    players_per_team: Optional[int] = Field(alias="players_per_team", default=None)

    cvars: Optional[Any] = Field(alias="cvars", default=None)

    message_id: Optional[str] = Field(alias="message_id", default=None)

    created_at: str = Field(alias="created_at")

    updated_at: str = Field(alias="updated_at")

    author: Optional[str] = Field(alias="author", default=None)

    server: Optional[str] = Field(alias="server", default=None)
