from enum import Enum


class TurboActionEnum(Enum):
    APPEND = "append"
    PREPEND = "prepend"
    REPLACE = "replace"
    UPDATE = "update"
    REMOVE = "remove"