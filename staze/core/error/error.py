from typing import Callable


class Error(Exception):
    """Main error class to be inherited in all app's custom errors.
    
    Args:
        message (str, optional):
            Message of the error. Defaults to cls.DEFAULT_MESSAGE
        status_code (int, optional):
            Status code of the error. Defaults to cls.DEFAULT_STATUS_CODE

    Attributes:
        message (str):
            Message of the error. Defaults to cls.DEFAULT_MESSAGE
        status_code (int):
            Status code of the error. Defaults to cls.DEFAULT_STATUS_CODE

    Raises:
        TypeError:
            If message or status code types are incorrect.
    """
    DEFAULT_MESSAGE = ''
    DEFAULT_STATUS_CODE = 400
    HANDLER_FUNCTION: Callable | None = None
    SHOULD_BE_LOGGED: bool = True

    def __init__(
            self,
            message: str | None = None,
            status_code: int | None = None) -> None:
        super().__init__(message)

        self.message: str
        self.status_code: int

        if message is None:
            self.message = self.DEFAULT_MESSAGE
        elif type(message) is str:
            self.message = message
        else:
            raise TypeError(
                'Error first argument (message) should be str,'
                f' got {type(message)} instead')

        if status_code is None:
            self.status_code = self.DEFAULT_STATUS_CODE
        elif type(status_code) is int:
            self.status_code: int = status_code
        else:
            raise TypeError(
                'Error second argument (status_code) should be int,'
                f' got {type(status_code)} instead')

    def expose(self) -> dict:
        """Expose error to structured dict for API.

        Returns:
            dict:
                Dictionary with structure:
        ```
        {
            'error': {
                'name': error_class_name,
                'message': error_message,
                'status_code': error_status_code
            }
        }
        ```
        """
        return {"error": {
            "name": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code
        }}

    def __str__(self) -> str:
        return self.message
