from staze import Sv, log


class UserSv(Sv):
    def __init__(self, config: dict) -> None:
        super().__init__(config)

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
