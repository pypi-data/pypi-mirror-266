from typing import *

from pydantic import BaseModel, Field

from .Match import Match


class PaginatedMatchList(BaseModel):
    """
    None model

    """

    count: int = Field(alias="count")

    next: Optional[str] = Field(alias="next", default=None)

    previous: Optional[str] = Field(alias="previous", default=None)

    results: List[Match] = Field(alias="results")
