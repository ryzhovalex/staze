from ..core.error.error import Error


class NotFoundError(Error):
    def __init__(
            self,
            message: str = 'Requested resource is not found',
            status_code: int = 404) -> None:
        super().__init__(message, status_code)
