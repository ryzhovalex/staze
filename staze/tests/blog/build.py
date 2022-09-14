__version__ = '0.0.0'

import secrets

from staze import Build, Service, Sock, View
from staze.core.database.database import Database
from staze.core.log.log import log
from staze.tests.blog.app.post.post_orm import PostOrm
from staze.tests.blog.app.tag.tag_orm import TagOrm
from staze.tests.blog.app.user.user_orm import UserOrm
from staze.tests.blog.app.user.user_service import UserService
from staze.tests.blog.app.user.user_view import UsersIdView


def create_all():
    Database.instance().create_all()

def add_user():
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
    config_dir='./configs',
    service_classes=service_classes,
    view_classes=view_classes,
    executables=[create_all, add_user]
)
