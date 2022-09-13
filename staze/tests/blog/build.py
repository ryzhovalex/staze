__version__ = '0.0.0'

import os
import sys
import secrets

from staze.core.database.database import Database
from staze.tests.blog.app.user.user_view import UsersIdView

# Add parent dir of app's dir
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from staze import (
    Build, Service, View, Sock)

from staze.tests.blog.app.user.user_service import UserService


def add_user():
    from staze.tests.blog.app.user.user_orm import UserOrm
    from staze.core.log.log import log

    username: str = secrets.token_hex(16)
    log.info(f'Add user {username}')
    user_orm: UserOrm = UserOrm.create(
        username=username, password='helloworld')
    Database.instance().push(user_orm) 


service_classes: list[type[Service]] = [
    UserService
]

view_classes: list[type[View]] = [
    UsersIdView
]

build = Build(
    version=__version__,
    service_classes=service_classes,
    view_classes=view_classes,
    executables=[add_user]
)
