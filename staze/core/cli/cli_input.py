from typing import Callable
from staze.core.app.app_mode_enum import AppModeEnumUnion
from staze.core.constants import DEFAULT_HOST, DEFAULT_PORT
from staze.core.model.model import Model


class CliInput(Model):
    mode_enum: AppModeEnumUnion
    args: list[str]
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    executables_to_execute: list[str] = []
