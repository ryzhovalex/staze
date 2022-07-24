from typing import TYPE_CHECKING

from flask_socketio import (
    SocketIO, send, emit, join_room, leave_room, SocketIOTestClient)

from staze.core.service.service import Service
from staze.core.log import log

if TYPE_CHECKING:
    from staze.core.app.app import App


class Socket(Service):
    def __init__(self, config: dict, app: 'App') -> None:
        super().__init__(config)
        self.app = app
        cors_allowed_origin = self.config.get('cors_allowed_origin', '*')

        log.info(f'Socket cors allowed: {cors_allowed_origin}')
        self.socketio: SocketIO = SocketIO(
            self.app.get_native_app(), cors_allowed_origins=cors_allowed_origin)

    def get_socketio(self) -> SocketIO:
        return self.socketio

    def get_test_client(self, namespace: str | None = None) -> SocketIOTestClient:
        return self.socketio.test_client(
            self.app.get_native_app(), namespace=namespace)

    def emit(
        self,
        event,
        data=None,
        room=None,
        include_self=True,
        namespace=None,
        callback=None) -> None:
        """Emit a custom event to one or more connected clients."""
        return self.socketio.emit(
            event, 
            data, 
            room=room,
            include_self=include_self,
            namespace=namespace,
            callback=callback)

    def send(
            self,
            data,
            room=None,
            include_self=True,
            namespace=None,
            callback=None,
            json=False) -> None:
        """Send a message to one or more connected clients."""
        return self.socketio.send(
            data,
            room=room,
            include_self=include_self,
            namespace=namespace,
            callback=callback,
            json=json)
