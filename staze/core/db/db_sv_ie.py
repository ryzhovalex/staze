from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass

from staze.core.service.service_ie import ServiceIe

if TYPE_CHECKING:
    from staze.core.database.database import Database


@dataclass
class DatabaseServiceIe(ServiceIe):
    """Injection cell with Database itself which can be applied to created
    application.
    """
    service_class: type[Database]