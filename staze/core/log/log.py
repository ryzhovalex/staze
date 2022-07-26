import os
from pydoc import classname
from typing import TYPE_CHECKING, Any, Callable, Literal

from loguru import logger as loguru
from loguru._logger import Logger
from warepy import Singleton
from staze.core.app.app_mode_enum import AppModeEnumUnion
from staze.core.log.layers.ecs import Ecs
from staze.core.log.layers.layer import Layer
from staze.core.log.log_error import LogError

if TYPE_CHECKING:
    from staze.core.service.service import Service


class log(Singleton):
    """Log tool responsible of writing all actions to logs.

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

    # TODO: Add support of custom log layers
    Layers: list[type[Layer]] = [Ecs]

    logger = loguru

    catch = logger.catch
    exception = logger.exception

    debug = logger.debug
    info = logger.info
    warning = logger.warning
    error = logger.error
    critical = logger.critical

    _mode_enum: AppModeEnumUnion
    _service_by_hash: dict[int, 'Service'] = {}

    @classmethod
    def setup(
            cls,
            *, 
            path: str, 
            format: str, 
            rotation: str, 
            level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            serialize: bool,
            layer: str | None = None,
            filter: Callable | str | dict | None = None,
            delete_old: bool = False
        ) -> int:
        """Init log model instance depending on given arguments. 

        Just a helpful method to recognize which arguments should be added with
        type hinting, and which is remain static.
        
        Remove previous old log if `delete_old=True`.

        Args:
            path:
                Path to log file to be storage for logs. Accept only string.
                If you want to pass other objects as loguru allows, use
                log.add()
            format:
                Format as loguru specifies
            rotation:
                Rotation as loguru specifies
            level:
                Level as loguru specifies
            serialize:
                Serialize as loguru specifies
            layer (optional):
                Specify layer to operate on logs. Every chosen layer stands
                as specific formatter and always saves logs to specified path.
                Defaults to None, i.e. default behaviour
            filter (optional):
                A directive optionally used to decide for each logged message
                whether it should be sent to the sink or not
            delete_old (optional):
                Flag whether is it required to remove old log file, specified under

        Returns:
            int:
                Id of created log handler. Useful to pass to log.remove()
        """
        # FIXME: Replace this logic to loguru.add.retention func
        if (
                delete_old
                and os.path.isfile(path)
                # Ensure that specified file is log for security
                and path.split('.')[-1] == 'log'):
            log.warning('Delete old log file')
            os.remove(path)

        sink: Callable | str
        layer_names: list[str] = [
            X.__name__.lower() for X in cls.Layers
        ]

        if layer is None or layer == 'default':
            sink = path
            return cls.logger.add(
                sink,
                format=format, 
                level=level,
                compression="zip", 
                rotation=rotation, 
                serialize=serialize,
                filter=filter
            )
        elif layer in layer_names:
            sink = cls._find_layer_by_name(layer)(
                    path=path,
                    mode_enum=cls._mode_enum,
                    compression='zip',
                    rotation=rotation,
                    service_by_hash=cls._service_by_hash
                ).format
            return cls.logger.add(
                # Warning here because of some error on overloaded types
                sink,  # type: ignore
                format=format, 
                level=level,
                serialize=serialize,
                filter=filter
            )
        else:
            raise LogError(f'Unrecognized layer: {layer}')

    @classmethod
    def _find_layer_by_name(cls, name: str) -> type[Layer]:
        for X in cls.Layers:
            if X.__name__.lower() == name:
                return X
        raise LogError(f'Unrecognized layer name: {name}')
