import os
from typing import Literal

from loguru import logger as loguru
from warepy import Singleton


class log(Singleton):
    """Logger tool responsible of writing all actions to logs.

    Simply said - it is a extra layer over `loguru.log` for keeping one log
    sink through all program.
    """
    DEFAULT_LOG_PARAMS = {
        "path": "./var/logs/system.log",
        "level": "DEBUG",
        "format":
            "{time:%Y.%m.%d at %H:%M:%S:%f%z} | {level} | {extra} >> {message}",
        "rotation": "10 MB",
        "serialize": False
    }

    native_log = loguru

    catch = native_log.catch

    debug = native_log.debug
    info = native_log.info
    warning = native_log.warning
    error = native_log.error
    critical = native_log.critical

    @classmethod
    def _create(cls, *args, **kwargs) -> int:
        return cls.native_log.add(*args, **kwargs)

    @classmethod
    def _remove(cls, id: int) -> None:
        cls.native_log.remove(id)

    @classmethod
    def get_native_log(cls):
        return cls.native_log

    @classmethod
    def bind(cls, **kwargs):
        return cls.native_log.bind(**kwargs)

    @classmethod
    def configure(
            cls,
            *, 
            path: str, 
            format: str, 
            rotation: str, 
            level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            serialize: bool,
            delete_old: bool = False) -> None:
        """Init log model instance depending on given arguments. 

        Just a helpful method to recognize which arguments should be added with
        type hinting, and which is remain static.
        
        Remove previous old log if `delete_old=True`.
        """
        # TODO: Add more clarified explanation/logic to this deletion.  It
        # should be either documented to user or refactored with security
        # considerations
        if (
                delete_old
                and os.path.isfile(path)
                # Ensure that specified file is log for security
                and path.split('.')[-1] == 'log'):
            os.remove(path)

        cls._create(
            path, 
            format=format, 
            level=level,
            compression="zip", 
            rotation=rotation, 
            serialize=serialize
        )


@log.catch
def raise_error_to_log(error: Exception) -> None:
    """Raise error with default logger catching."""
    raise error
