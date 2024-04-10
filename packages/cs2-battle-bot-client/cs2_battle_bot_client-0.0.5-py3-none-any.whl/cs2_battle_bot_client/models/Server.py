from typing import *

from pydantic import BaseModel, Field


class Server(BaseModel):
    """
    None model

    """

    id: str = Field(alias="id")

    name: str = Field(alias="name")

    ip: str = Field(alias="ip")

    port: int = Field(alias="port")

    password: Optional[str] = Field(alias="password", default=None)

    is_public: Optional[bool] = Field(alias="is_public", default=None)
