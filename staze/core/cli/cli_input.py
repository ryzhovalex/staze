from typing import Callable
from staze.core.app.app_mode_enum import AppModeEnumUnion
from staze.core.model.model import Model


class CliInput(Model):
    mode_enum: AppModeEnumUnion
    args: list[str]

    # Staze's mode args
    host: str = '127.0.0.1'
    port: int = 5000

    executables: list[Callable]
