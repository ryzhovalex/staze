from dataclasses import dataclass

from staze.core.ie.named_ie import NamedIe
from staze.core.sv.sv import Sv


@dataclass
class SvIe(NamedIe):
    sv_class: type[Sv]
