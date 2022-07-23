import os
from typing import Callable
from staze.tools.hints import CLIModeEnumUnion
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
    
    Should be inherited by build class in root folder.
    """
    def __init__(
            self,
            version: str = "",
            config_dir: str = "./src/configs",
            service_classes: list[type[Service]] = [],
            view_classes: list[type[View]] = [],
            error_classes: list[type[Error]] = [],
            shell_processors: list[Callable] = [],
            cli_cmds: list[Callable] = [],
            sock_classes: list[type[Sock]] = [],
            default_sock_error_handler: Callable = default_sock_error_handler,
            ctx_processor_func: Callable | None = None,
            each_request_func: Callable | None = None,
            first_request_func: Callable | None = None) -> None:
        self.version = version
        self.config_dir = config_dir
        self.service_classes = service_classes
        self.view_classes = view_classes
        self.error_classes = error_classes
        self.shell_processors = shell_processors
        self.cli_cmds = cli_cmds
        self.ctx_processor_func = ctx_processor_func
        self.each_request_func = each_request_func
        self.first_request_func = first_request_func
        self.sock_classes = sock_classes
        self.default_sock_error_handler = default_sock_error_handler

    def build_app(
            self,
            mode_enum: CLIModeEnumUnion,
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
