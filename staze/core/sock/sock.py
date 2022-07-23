from flask_socketio import SocketIO, Namespace
from staze.tools.log import log

from .socket import Socket


class Sock(Namespace):
    def __init__(self, namespace=None):
        super().__init__(namespace)
        self.socket: Socket = Socket.instance()

    def on_connect(self):
        self.socket.send('Connected')

    def on_disconnect(self):
        self.socket.send('Disconnected')

    def on_message(self, message):
        self.socket.send(f'Hello {message}!')
