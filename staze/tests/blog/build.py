__version__ = '0.0.0'

import os
import sys

# Add parent dir of app's dir
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from staze import (
    Build, Service, View, Sock)

from blog.app.user.user_service import UserService
from blog.tools.shell import import_main, import_std
from blog.app.user.user_view import UserView
from blog.app.chat.chat_service import ChatService
from blog.app.chat.chat_sock import ChatSock


service_classes: list[type[Service]] = [
    ChatService,
    UserService
]

sock_classes: list[type[Sock]] = [
    ChatSock
]

view_classes: list[type[View]] = [
    UserView
]

build = Build(
    version=__version__,
    service_classes=service_classes,
    view_classes=view_classes,
    shell_processors=[import_std, import_main],
    sock_classes=sock_classes)
