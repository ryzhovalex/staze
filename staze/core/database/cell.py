from dataclasses import dataclass, fields
from typing import Any, ClassVar

from schema import Schema
from staze.core.database.database import orm
from staze.tools.log import log
from staze.core.db.cell_error import CellError
from warepy import snakefy
from staze. core.model.model import Model


 
class Cell(Model):
    Model: ClassVar = None
    id: int
    type: str

    @classmethod
    def _get_formatted_name(cls, base_name: str = 'Cell') -> str:
        return super()._get_formatted_name(base_name)

    @classmethod
    def gen(cls, instance: orm.Model) -> 'Cell':
        return cls._gen_according(instance)

    @classmethod
    def _gen_according(cls, instance: orm.Model) -> Any:
        """Traverse all Models of all subclasses to find according to given
        type model cell.
        """
        cell_type_by_model_type: dict = {}
        subclasses: list[type] = cls.__subclasses__()
        model_type = type(instance)

        # Get models for cells from all inheritance tree
        cell_type_by_model_type.update(
            cls._get_ie_type_by_model_type(subclasses))

        try:
            cell_type = cell_type_by_model_type[model_type]
        except KeyError:
            raise CellError(
                f'Cannot find cell with requested model type: {model_type}\n'
                'Maybe you forgot to add `Model=...` to Model\'s definition?')
        else:
            return cell_type.gen_instance(instance)

    @classmethod
    def gen_instance(cls) -> 'Model':
        raise NotImplementedError('Should be re-implemented in child class')
        
    @classmethod
    def _get_ie_type_by_model_type(cls, subclasses: list) -> dict:
        cell_type_by_model_type: dict[type, type] = {}

        # Get own model
        if cls.Model is not None:
            cell_type_by_model_type[cls.Model] = cls

        # Traverse inheritance tree
        for subclass in subclasses:
            cell_type_by_model_type.update(
                subclass._get_ie_type_by_model_type(
                    subclass.__subclasses__()))

        return cell_type_by_model_type