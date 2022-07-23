from staze.core.error.error import Error


class ModelNotFoundError(Error):
    def __init__(
            self,
            model_name: str,
            message: str = '',
            status_code: int = 404,
            **used_parameters) -> None:
        super().__init__(message, status_code)
        if message == '':
            self.message = \
                f"No model {model_name} with such" \
                f" parameters: {used_parameters}"
