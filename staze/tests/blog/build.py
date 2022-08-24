__version__ = '0.0.0'

import os
import sys

# Add parent dir of app's dir
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from staze import (
    Build, Service, View, Sock)

from staze.tests.blog.app.user.user_service import UserService


service_classes: list[type[Service]] = [
    UserService
]

view_classes: list[type[View]] = [
]

build = Build(
    version=__version__,
    service_classes=service_classes,
    view_classes=view_classes)
