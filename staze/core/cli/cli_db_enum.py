from enum import Enum


class CLIDatabaseEnum(Enum):
    INIT = "init"
    MIGRATE = "migrate"
    UPGRADE = "upgrade"