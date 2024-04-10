from typing import *

from pydantic import BaseModel, Field


class Nested(BaseModel):
    """
    None model

    """

    id: str = Field(alias="id")

    user_id: str = Field(alias="user_id")

    username: str = Field(alias="username")

    created_at: str = Field(alias="created_at")

    updated_at: str = Field(alias="updated_at")
