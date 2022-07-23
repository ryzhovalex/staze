from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass

from staze.core.sv.sv_ie import SvIe

if TYPE_CHECKING:
    from staze.core.sock.socket import Socket


@dataclass
class SocketSvIe(SvIe):
    sv_class: type[Socket]
