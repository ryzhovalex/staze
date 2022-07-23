from dataclasses import dataclass
from staze. core.model.model import Model
from staze.tools.hints import CLIModeEnumUnion


 
class CLIInputModel(Model):
    mode_enum: CLIModeEnumUnion
    mode_args: list[str]

    # Staze's mode args
    host: str = '127.0.0.1'
    port: int = 5000
