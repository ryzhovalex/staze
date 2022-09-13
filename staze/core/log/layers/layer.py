import json
from loguru._handler import Message
from flask import request


class Layer:
    """Layer to operate with logs.
    
    Args:
        path:
            Path to file to save formatted logs to.
        compression (optional):
            Compression format to which log files should be converted.
        rotation (optional):
            Condition indicating wheneve the current logged file should be
            closed and a new one started. 
    """

    def __init__(
                self,
                path: str,
                compression: str | None = None,
                rotation: str | None = None
            ) -> None:
        self._path = path
        self._compression = compression
        self._rotation = rotation

    def _populate_with_request_context(self, log_extra: dict) -> None:
        try:
            print(request.__dict__)
        except RuntimeError:
            pass

    def _write(self, log: dict) -> None:
        with open(self._path, 'a+') as file:
            json.dump(log, file)

    def format(self, message: Message) -> None:
        raise NotImplementedError(
            'Should be re-implemented at the children class')
