import re
from typing import Any
from enum import EnumMeta
from staze.core.log import log
from staze.core.validation.validation_error import (
    ValidationError, ReValidationError)


def validate(
        obj: Any, expected_type: type | list[type],
        obj_name: str = 'Entity', strict: bool = False) -> None:
    if isinstance(expected_type, type):
        if strict:
            if type(obj) is not expected_type:
                raise ValidationError(obj_name, expected_type)
        else:
            if not isinstance(obj, expected_type):
                raise ValidationError(obj_name, expected_type)
    elif type(expected_type) is list:
        found: bool = False

        for type_ in expected_type:
            if type(obj) is type_:
                found = True
        
        if not found:
            raise ValidationError(obj_name, expected_type)
    else:
        raise TypeError('Expected type should be `type` type')


def validate_re(string: str, pattern: str) -> None:
    """Validate given string using re.match.
    
    Raises:
        ValidationError:
            String does not match given pattern.
    """
    if not re.match(pattern, string):
        raise ReValidationError(validated_name=string, pattern=pattern)
