from enum import Enum
from staze.core.model.model import Model


class RunAppModeEnum(Enum):
    DEV = "dev"
    PROD = "prod"
    TEST = "test"


class DatabaseAppModeEnum(Enum):
    INIT = "init"
    MIGRATE = "migrate"
    UPGRADE = "upgrade"


class HelperAppModeEnum(Enum):
    SHELL = 'shell'
    DEPLOY = 'deploy'
    VERSION = 'version'

    # Custom cmds
    CMD = 'cmd'


AppModeEnumUnion = DatabaseAppModeEnum | RunAppModeEnum | HelperAppModeEnum
