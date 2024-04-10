from typing import *

from pydantic import BaseModel, Field


class PatchedMap(BaseModel):
    """
    None model

    """

    id: Optional[str] = Field(alias="id", default=None)

    name: Optional[str] = Field(alias="name", default=None)

    tag: Optional[str] = Field(alias="tag", default=None)

    created_at: Optional[str] = Field(alias="created_at", default=None)

    updated_at: Optional[str] = Field(alias="updated_at", default=None)
