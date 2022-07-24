from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from staze.core.service.service_ie import ServiceModel

if TYPE_CHECKING:
    from staze.core.app.app import Staze
    from staze.core.hints import CLIModeEnumUnion

 
class StazeServiceModel(ServiceModel):
    """Injection cell with app itself which is required in any build."""
    service_class: type[Staze]
    mode_enum: CLIModeEnumUnion
    host: str
    port: int
    ctx_processor_func: Callable | None = None
    each_request_func: Callable | None = None
    first_request_func: Callable | None = None
