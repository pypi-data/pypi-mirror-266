from typing import *

from pydantic import BaseModel, Field


class Map(BaseModel):
    """
    None model

    """

    id: str = Field(alias="id")

    name: str = Field(alias="name")

    tag: str = Field(alias="tag")

    created_at: str = Field(alias="created_at")

    updated_at: str = Field(alias="updated_at")
