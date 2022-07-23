from dataclasses import dataclass
from staze.core.ie.ie import Ie
from staze.tools.hints import CLIModeEnumUnion


@dataclass
class CLIInputIe(Ie):
    mode_enum: CLIModeEnumUnion
    mode_args: list[str]

    # Staze's mode args
    host: str = '127.0.0.1'
    port: int = 5000
