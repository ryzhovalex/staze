from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass

from staze.core.service.service_ie import ServiceModel

if TYPE_CHECKING:
    from staze.core.sock.socket import Socket


 
class SocketServiceModel(ServiceModel):
    service_class: type[Socket]
