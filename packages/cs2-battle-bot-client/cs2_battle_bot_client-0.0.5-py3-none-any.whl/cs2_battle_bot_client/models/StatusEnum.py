from enum import Enum


class StatusEnum(str, Enum):

    CREATED = "CREATED"
    STARTED = "STARTED"
    LIVE = "LIVE"
    FINISHED = "FINISHED"
