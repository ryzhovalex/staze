from staze import Service, log


class UserService(Service):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        
        # Variables to test service dict logging
        self._request_log_a: int = 2
        self._request_log_b: str = 'helloworld'

    def request_log(self) -> None:
        self.log.info('Log arbitrary data about user service')

    def get_license_number(self) -> int:
        try:
            return self.config['license_number']
        except KeyError:
            raise KeyError('License number is not defined in config')

    def get_user_system_token(self) -> str:
        try:
            return self.config['user_system_token']
        except KeyError:
            raise KeyError('Pc hostname is not defined in config')
