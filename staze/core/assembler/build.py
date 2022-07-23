import os
from typing import Callable
from staze.tools.hints import CLIModeEnumUnion
from staze.core.app.app import Staze
from staze.core.assembler.assembler import Assembler
from staze.core.sock.default_sock_error_handler import default_sock_error_handler
from staze.core.sock.sock_ie import SockIe

from staze.core.sv.sv_ie import SvIe
from staze.core.view.view_ie import ViewIe
from staze.core.emt.emt_ie import EmtIe
from staze.core.error.error_ie import ErrorIe


class Build:
    """Proxy mapping class with collection of initial project instances to be
    builded by assembler.
    
    Should be inherited by build class in root folder.
    """
    def __init__(
        self,
        version: str = "",
        config_dir: str = "./src/configs",
        sv_ies: list[SvIe] = [],
        view_ies: list[ViewIe] = [],
        emt_ies: list[EmtIe] = [],
        error_ies: list[ErrorIe] = [],
        shell_processors: list[Callable] = [],
        cli_cmds: list[Callable] = [],
        sock_ies: list[SockIe] = [],
        default_sock_error_handler: Callable = default_sock_error_handler,
        ctx_processor_func: Callable | None = None,
        each_request_func: Callable | None = None,
        first_request_func: Callable | None = None,
    ) -> None:
        self.version = version
        self.config_dir = config_dir
        self.sv_ies = sv_ies
        self.view_ies = view_ies
        self.emt_ies = emt_ies
        self.error_ies = error_ies
        self.shell_processors = shell_processors
        self.cli_cmds = cli_cmds
        self.ctx_processor_func = ctx_processor_func
        self.each_request_func = each_request_func
        self.first_request_func = first_request_func
        self.sock_ies = sock_ies
        self.default_sock_error_handler = default_sock_error_handler

    def build_app(
            self,
            mode_enum: CLIModeEnumUnion,
            host: str = 'localhost',
            port: int = 5000,
            root_dir: str = os.getcwd()) -> Staze:
        """Allows manually build assembler without immediate app running."""
        assembler = Assembler(
            mode_enum=mode_enum,
            host=host,
            port=port,
            root_dir=root_dir,
            build=self)
        return assembler.staze
