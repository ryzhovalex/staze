from dataclasses import dataclass, fields
from typing import Any, Iterable
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

    @property
    def api_dict(self) -> dict:
        return self.get_api_dict()

    def get_api_dict(
            self,
            formatted_name: str | None = None,
            is_without_formatted_name: bool = False) -> dict:
        """Translates interface to dict structure for API.
        
        Args:
            formatted_name (str, optional):
                Custom formatted name as external dictionary key.
                Defaults to class's base defined (property formatted_name).
            is_without_formatted_name(str, optional):
                If True, dict without external key is returned, but note that
                nested models still will have such external key.
                If you don't need any external keys for nested models, use
                standard Pydantic dict() instead.
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
        formatted_dict: dict = {}

        if formatted_name:
            _formatted_name = formatted_name  
        else:
            _formatted_name = self._get_formatted_name()

        for k, v in self.__dict__.items():
            alias: str = k
            if isinstance(v, Model):
                alias = v.formatted_name
            
            formatted_dict[alias] = self._parse_value(v)

        if is_without_formatted_name:
            return formatted_dict
        else:
            return {
                _formatted_name: formatted_dict
            }

    def _parse_value(
            self, v: Any) -> Any:
        final_value: Any

        if isinstance(v, Model):
            final_value = v.get_api_dict(is_without_formatted_name=True)
        # Not passed for cases of missing attr and empty dict.
        # I.e. classes with empty dict returned from __dict__ skipping
        # this branch
        elif getattr(v, "__dict__", None):
            final_value = v.__dict__
        elif \
                isinstance(v, Iterable) \
                and (hasattr(v, "append") or hasattr(v, "push")):
            final_value = type(v)()
            for element in v:
                parsed_element: Any
                if isinstance(element, Model):
                    parsed_element = {
                        element.formatted_name: self._parse_value(element)
                    }
                else:
                    parsed_element = self._parse_value(element)

                if hasattr(v, "append"):
                    # Call again but for every list element
                    final_value.append(parsed_element)
                else:
                    # In theory, set could be iterable with `push` operation
                    # but set cannot store unhashable types so it doesn't
                    # make sense. But custom iterables may still implement
                    # `push` method
                    final_value.push(parsed_element)
        else:
            final_value = v

        return final_value

    @classmethod
    def _get_formatted_name(cls) -> str:
        name: str

        if cls._formatted_name:
            name = cls._formatted_name
        else:
            name = snakefy(cls.__name__.replace(cls._base_name, ''))

        return name
