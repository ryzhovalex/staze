from enum import Enum


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
    EXEC = 'exec'


AppModeEnumUnion = DatabaseAppModeEnum | RunAppModeEnum | HelperAppModeEnum
