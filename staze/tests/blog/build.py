__version__ = '0.0.0'

import os
import sys

# Add parent dir of app's dir
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from staze import (
    Build, ServiceModel, ViewModel, SockModel, log)

from blog.app.user.user_service import UserService
from blog.tools.shell import import_main, import_std
from blog.app.user.user_view import UserView
from blog.app.chat.chat_service import ChatService
from blog.app.chat.chat_sock import ChatSock


service_ies: list[ServiceModel] = [
    ServiceModel('user', UserService),
    ServiceModel('chat', service_class=ChatService)
]

sock_ies: list[SockModel] = [
    SockModel('/chat', ChatSock)
]

view_ies: list[ViewModel] = [
    ViewModel('/user/<id>', UserView)
]

build = Build(
    version=__version__,
    service_ies=service_ies,
    view_ies=view_ies,
    shell_processors=[import_std, import_main],
    sock_ies=sock_ies)
