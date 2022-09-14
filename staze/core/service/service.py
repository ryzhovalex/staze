from warepy import Singleton
from staze.core.log.log import log
from staze.core.log.log_snapshot_field_spec_enum import LogSnapshotFieldSpecEnum


class Service(Singleton):
    """Service superclass inherits Singleton metaclass.

    Layer between Domain Objects (Domains) and UI layer
    (Controllers and Views).
    Performs various operations e.g. to prepare data (like json formatting)
    coming to Domains and from them.
    """
    # Name of config to be fetched for this service, if None, builded from
    # class name with excluded BASE_NAME, e.g.: 'UserService' -> 'user',
    # and thus e.g. `user.yaml` will be searched in config folder
    CONFIG_NAME: str | None = None
    BASE_NAME: str = 'Service'

    # Whether snapshots can be made from this service by log layers. Note that
    # this settings is applied for every subobject's dict, so private fields
    # of subobjects with according setting won't be part of snapshot too
    LOG_SNAPSHOT_RULES: dict[str, LogSnapshotFieldSpecEnum] = {
        'public': LogSnapshotFieldSpecEnum.ALWAYS,
        'protected': LogSnapshotFieldSpecEnum.ALWAYS,
        'private': LogSnapshotFieldSpecEnum.ALWAYS
    }

    def __init__(self, config: dict) -> None:
        self.config = config
        self.log = log.bind(service_hash=hash(self))

    @classmethod
    def get_config_name(cls) -> str:
        if cls.CONFIG_NAME:
            return cls.CONFIG_NAME
        else:
            return cls.__name__.replace(cls.BASE_NAME, '').lower()
