from dataclasses import dataclass
from typing import Callable

from staze. core.model.model import Model
from .sock import Sock
from .default_sock_error_handler import default_sock_error_handler


 
class SockModel(Model):
    namespace: str
    handler_class: type[Sock]
    error_handler: Callable = default_sock_error_handler
