import json
from abc import abstractmethod
from typing import Any, List, Dict, Literal, Union, Callable, Type

from warepy import Singleton, format_message
from staze.tools.log import log


class Sv(Singleton):
    """Sv superclass inherits Singleton metaclass.

    Layer between Domain Objects (Domains) and UI layer (Controllers and Views).
    Performs various operations e.g. to prepare data (like json formatting) coming to Domains and from them."""
    def __init__(self, config: dict) -> None:
        self.config = config
