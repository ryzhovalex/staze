from dataclasses import dataclass, fields
from typing import Any
import types
from staze.tools.log import log
from typing import ClassVar
from warepy import snakefy
from pydantic import BaseModel


class Model(BaseModel):
    """Basic interface dataclass."""
    _formatted_name: ClassVar[str | None] = None

    @property
    def formatted_name(self) -> str:
        return self._get_formatted_name()

    def get_json(self, formatted_name: str | None = None) -> dict:
        """Translates interface to dict structure for API.
        
        Args:
            formatted_name (str, optional):
                Custom formatted name as external dictionary key.
                Defaults to class's base defined (property formatted_name).

        Returns:
            dict:
                Dictionary with interface decomposed to structure for API:
        ```
        {
           model_formatted_name: {
                ...model structure    
            }
        }
        ```
        """
        _formatted_name: str

        if formatted_name:
            _formatted_name = formatted_name  
        else:
            _formatted_name = self._get_formatted_name()

        return {
            _formatted_name: self._get_decomposed_dict()
        }

    def get_inner_json(self) -> dict:
        """Return json without header."""
        return self._get_decomposed_dict()

    def _get_decomposed_dict(self) -> dict:
        res_dict: dict = {}

        # Decompose all keys in self dict
        for k, v in self.__dict__.items():
            if type(v) is Model:
                # For folded Models make their own json decompositions
                res_dict[k] = v.get_inner_json()
            else:
                res_dict[k] = v

        return res_dict

    @classmethod
    def get_json_types(cls) -> dict:
        # https://stackoverflow.com/a/51953411/14748231
        return {
            cls._get_formatted_name(): {
                field.name: field.type for field in fields(cls)
            }
        }

    @classmethod
    def _get_formatted_name(cls, base_name: str = 'Model') -> str:
        name: str

        if cls.FORMATTED_NAME:
            name = cls.FORMATTED_NAME
        else:
            name = snakefy(cls.__name__.replace(base_name, ''))

        return name

    @classmethod
    def _fetch_schema_types(cls, data: dict) -> dict:
        schema_types: dict = {}

        for k, v in data.items():
            if type(v) is dict:
                # Call self recusively if another dict encountered
                schema_types[k] = cls._fetch_schema_types(v)
            elif type(v) is types.UnionType:
                # Unpack arguments (classes) of union into schema's `Or`
                # statement
                schema_types[k] = Or(*v.__args__)
            else:
                # Others go normally
                schema_types[k] = v

        # All other keys does not matter and optional - useful for checking
        # child classes under base class calling procedure
        schema_types.update({Optional(str): object})

        return schema_types

    @classmethod
    def get_schema(cls) -> Schema:
        schema_types: dict = \
            cls._fetch_schema_types(cls.get_json_types())
        return Schema(schema_types)

    @classmethod
    def validate(cls, data: dict, **kwargs) -> None:
        cls.get_schema().validate(data, **kwargs)
