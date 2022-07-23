from enum import Enum


class CLIHelperEnum(Enum):
    SHELL = 'shell'
    DEPLOY = 'deploy'
    VERSION = 'version'

    # Custom cmds
    CMD = 'cmd'
