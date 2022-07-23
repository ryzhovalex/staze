from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from staze.core.sv.sv_ie import SvIe

if TYPE_CHECKING:
    from staze.core.app.app import Staze
    from staze.tools.hints import CLIModeEnumUnion


@dataclass
class StazeSvIe(SvIe):
    """Injection cell with app itself which is required in any build."""
    sv_class: type[Staze]
    mode_enum: CLIModeEnumUnion
    host: str
    port: int
    ctx_processor_func: Callable | None = None
    each_request_func: Callable | None = None
    first_request_func: Callable | None = None