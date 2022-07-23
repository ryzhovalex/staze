__version__ = '0.0.0'

import os
import sys

# Add parent dir of app's dir
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from staze import (
    Build, SvIe, ViewIe, SockIe, log)

from blog.app.user.user_sv import UserSv
from blog.tools.shell import import_main, import_std
from blog.app.user.user_view import UserView
from blog.app.chat.chat_sv import ChatSv
from blog.app.chat.chat_sock import ChatSock


sv_ies: list[SvIe] = [
    SvIe('user', UserSv),
    SvIe('chat', sv_class=ChatSv)
]

sock_ies: list[SockIe] = [
    SockIe('/chat', ChatSock)
]

view_ies: list[ViewIe] = [
    ViewIe('/user/<id>', UserView)
]

build = Build(
    version=__version__,
    sv_ies=sv_ies,
    view_ies=view_ies,
    shell_processors=[import_std, import_main],
    sock_ies=sock_ies)
