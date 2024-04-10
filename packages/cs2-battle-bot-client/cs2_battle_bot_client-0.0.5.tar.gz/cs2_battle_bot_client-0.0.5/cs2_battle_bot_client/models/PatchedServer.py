from typing import *

from pydantic import BaseModel, Field


class PatchedServer(BaseModel):
    """
    None model

    """

    id: Optional[str] = Field(alias="id", default=None)

    name: Optional[str] = Field(alias="name", default=None)

    ip: Optional[str] = Field(alias="ip", default=None)

    port: Optional[int] = Field(alias="port", default=None)

    password: Optional[str] = Field(alias="password", default=None)

    is_public: Optional[bool] = Field(alias="is_public", default=None)
