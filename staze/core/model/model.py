from dataclasses import dataclass, fields
from typing import Any
import types
from staze.core.log import log
from typing import ClassVar
from warepy import snakefy
from pydantic import BaseModel


class Model(BaseModel):
    """Basic interface dataclass."""
    # Name to be excluded from final formatted name
    _base_name: str = 'Model'
    _formatted_name: str | None = None

    @property
    def formatted_name(self) -> str:
        return self._get_formatted_name()

    def get_api_dict(self, formatted_name: str | None = None) -> dict:
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
            _formatted_name: self.dict()
        }

    @classmethod
    def _get_formatted_name(cls) -> str:
        name: str

        if cls._formatted_name:
            name = cls._formatted_name
        else:
            name = snakefy(cls.__name__.replace(cls._base_name, ''))

        return name
