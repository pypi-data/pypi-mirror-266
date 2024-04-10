from typing import *

from pydantic import BaseModel, Field

from .Map import Map
from .MapBan import MapBan
from .MatchMapSelected import MatchMapSelected
from .StatusEnum import StatusEnum
from .Team import Team
from .TypeEnum import TypeEnum


class PatchedMatch(BaseModel):
    """
    None model

    """

    id: Optional[int] = Field(alias="id", default=None)

    team1: Optional[Team] = Field(alias="team1", default=None)

    team2: Optional[Team] = Field(alias="team2", default=None)

    winner_team: Optional[Team] = Field(alias="winner_team", default=None)

    maps: Optional[List[Optional[Map]]] = Field(alias="maps", default=None)

    map_bans: Optional[List[Optional[MapBan]]] = Field(alias="map_bans", default=None)

    map_picks: Optional[List[Optional[MatchMapSelected]]] = Field(alias="map_picks", default=None)

    connect_command: Optional[str] = Field(alias="connect_command", default=None)

    load_match_command: Optional[str] = Field(alias="load_match_command", default=None)

    status: Optional[StatusEnum] = Field(alias="status", default=None)

    type: Optional[TypeEnum] = Field(alias="type", default=None)

    num_maps: Optional[int] = Field(alias="num_maps", default=None)

    maplist: Optional[Any] = Field(alias="maplist", default=None)

    map_sides: Optional[Any] = Field(alias="map_sides", default=None)

    clinch_series: Optional[bool] = Field(alias="clinch_series", default=None)

    players_per_team: Optional[int] = Field(alias="players_per_team", default=None)

    cvars: Optional[Any] = Field(alias="cvars", default=None)

    message_id: Optional[str] = Field(alias="message_id", default=None)

    created_at: Optional[str] = Field(alias="created_at", default=None)

    updated_at: Optional[str] = Field(alias="updated_at", default=None)

    author: Optional[str] = Field(alias="author", default=None)

    server: Optional[str] = Field(alias="server", default=None)
