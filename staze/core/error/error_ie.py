from typing import Callable
from dataclasses import dataclass

from staze. core.model.model import Model

from .error import Error


 
class ErrorModel(Model):
    error_class: type[Error]
    handler_function: Callable
