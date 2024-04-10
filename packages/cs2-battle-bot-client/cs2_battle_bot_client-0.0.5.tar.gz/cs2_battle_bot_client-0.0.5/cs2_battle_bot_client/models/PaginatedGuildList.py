from typing import *

from pydantic import BaseModel, Field

from .Guild import Guild


class PaginatedGuildList(BaseModel):
    """
    None model

    """

    count: int = Field(alias="count")

    next: Optional[str] = Field(alias="next", default=None)

    previous: Optional[str] = Field(alias="previous", default=None)

    results: List[Guild] = Field(alias="results")
