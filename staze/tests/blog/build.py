__version__ = '0.0.0'

import os
import sys

# Add parent dir of app's dir
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from staze import (
    Build, Service, View, Sock)

from staze.tests.blog.app.user.user_service import UserService
from blog.app.user.user_view import UsersIdView


service_classes: list[type[Service]] = [
    UserService
]

sock_classes: list[type[Sock]] = [
]

view_classes: list[type[View]] = [
    UsersIdView
]

build = Build(
    version=__version__,
    service_classes=service_classes,
    view_classes=view_classes,
    sock_classes=sock_classes)
