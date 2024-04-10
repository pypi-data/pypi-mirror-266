from typing import *

from pydantic import BaseModel, Field

from .Player import Player


class PaginatedPlayerList(BaseModel):
    """
    None model

    """

    count: int = Field(alias="count")

    next: Optional[str] = Field(alias="next", default=None)

    previous: Optional[str] = Field(alias="previous", default=None)

    results: List[Player] = Field(alias="results")
