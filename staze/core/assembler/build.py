import os
from typing import Callable
from staze.core.app.app_mode_enum import AppModeEnumUnion
from staze.core.app.app import App
from staze.core.assembler.assembler import Assembler
from staze.core.socket.default_sock_error_handler import (
    default_sock_error_handler)
from staze.core.service.service import Service
from staze.core.view.view import View
from staze.core.error.error import Error
from staze.core.socket.sock import Sock


class Build:
    """Proxy mapping class with collection of initial project instances to be
    builded by assembler.

    Args:
        version (optional):
            Version of the project. Defaults to '0.0.0'
        env_path (optional):
            Path to file with environment variables. Defaults to '.env'
        config_dir (optional):
            Directory of configuration files. Defaults to './src/configs'
        service_classes (optional):
            List of Service classes to be initialized. Defaults to empty list
        view_classes (optional):
            List of View classes to be initialized. Defaults to empty list
        sock_classes (optional):
            List of Sock classes to be initialized. Defaults to empty list
        shell_processors (optional):
            List of Callables that will serve shell processor function. Note
            that shell processor callable should return dictionary with
            namespace for the shell.
            Defaults to empty list
        default_error_handler (optional):
            Callable to be called on Error reaching top level of program.
            Defaults to None, e.g. app's default logic will be used
        default_builtin_error_handler (optional):
            Callable to be called on Exception reaching top level of program.
            Defaults to None, e.g. app's default logic will be used
        ctx_processor_func (optional):
            Callable to be called on Flask.context_processor.
            Defaults to None
        each_request_func (optional):
            Callable to be called on Flask.before_request.
            Defaults to None
        first_request_func (optional):
            Callable to be called on Flask.before_first_request.
            Defaults to None
    """
    def __init__(
            self,
            *,
            version: str = '0.0.0',
            env_path: str = '.env',
            config_dir: str = './src/configs',
            service_classes: list[type[Service]] = [],
            view_classes: list[type[View]] = [],
            shell_processors: list[Callable] = [],
            sock_classes: list[type[Sock]] = [],
            default_error_handler: Callable | None = None,
            default_builtin_error_handler: Callable | None = \
                None,
            ctx_processor_func: Callable | None = None,
            each_request_func: Callable | None = None,
            first_request_func: Callable | None = None) -> None:
        self.version = version
        self.env_path = env_path
        self.config_dir = config_dir
        self.service_classes = service_classes
        self.view_classes = view_classes
        self.shell_processors = shell_processors
        self.ctx_processor_func = ctx_processor_func
        self.each_request_func = each_request_func
        self.first_request_func = first_request_func
        self.sock_classes = sock_classes
        self.default_error_handler = default_error_handler
        self.default_builtin_error_handler = default_builtin_error_handler

    def build_app(
            self,
            mode_enum: AppModeEnumUnion,
            host: str = 'localhost',
            port: int = 5000,
            root_dir: str = os.getcwd()) -> App:
        """Allows manually build assembler without immediate app running."""
        assembler = Assembler(
            mode_enum=mode_enum,
            host=host,
            port=port,
            root_dir=root_dir,
            build=self)
        return assembler.app
