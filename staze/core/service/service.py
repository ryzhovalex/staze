from warepy import Singleton
from staze.tools.log import log


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
    _CONFIG_NAME: str | None = None
    _BASE_NAME: str = 'Service'

    def __init__(self, config: dict) -> None:
        self.config = config

    @classmethod
    def get_config_name(cls) -> str:
        if cls._CONFIG_NAME:
            return cls._CONFIG_NAME
        else:
            return cls.__name__.replace(cls._BASE_NAME, '').lower()
