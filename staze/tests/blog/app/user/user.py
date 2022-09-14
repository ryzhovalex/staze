from staze.core.model.model import Model


class User(Model):
    id: int
    type: str
    username: str
