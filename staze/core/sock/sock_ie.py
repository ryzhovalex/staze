from dataclasses import dataclass
from typing import Callable

from staze.core.ie.ie import Ie
from .sock import Sock
from .default_sock_error_handler import default_sock_error_handler


@dataclass
class SockIe(Ie):
    namespace: str
    handler_class: type[Sock]
    error_handler: Callable = default_sock_error_handler
