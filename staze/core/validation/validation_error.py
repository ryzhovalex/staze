from typing import Any
from staze.core.error.error import Error


class ValidationError(Error):
    def __init__(
            self,
            validated_name: str,
            expected_type: type | list[type],
            message: str | None = None,
            status_code: int | None = None) -> None:
        super().__init__(message, status_code)

        if message is None:
            if isinstance(expected_type, type):
                self.message = \
                    f'{validated_name} should have type:' \
                    f' {expected_type.__name__}'
            elif type(expected_type) is list:
                self.message = \
                    f'{validated_name} should have one type of the following' \
                    f' list: {[type_.__name__ for type_ in expected_type]}'
            else:
                raise TypeError('Unrecognized type of `expected_type`')


# ReValidationError inherits base Error, not ValidationError, since some old
# features differ from ValidationError
class ReValidationError(Error):
    def __init__(
            self,
            validated_name: str,
            pattern: str,
            message: str | None = None,
            status_code: int | None = None) -> None:
        super().__init__(message, status_code)
        
        if message is None:
            self.message = \
                f'{validated_name} should implement pattern {pattern}'
