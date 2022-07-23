from dataclasses import dataclass

from staze. core.model.model import Model

from .emt import Emt


 
class EmtModel(Model):
    emt_class: type[Emt]