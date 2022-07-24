from typing import Callable
from pytest import fixture
from flask_socketio import SocketIOTestClient
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from staze.core.app.app import App
from staze.core import validation, parsing
from staze.core.database.database import Database
from staze.core.socket.socket import Socket
from staze.core.test.http_client import HttpClient


class Test:
    @fixture
    def http(self, app: App, client: FlaskClient) -> HttpClient:
        return HttpClient(client)

    @fixture
    def app(self):
        app: App = App.instance()
        yield app

    @fixture
    def db(self, app: App):
        database: Database = Database.instance()

        with app.app_context():
            database.drop_all()
            database.create_all()

        yield database

        with app.app_context():
            database.drop_all()

    @fixture
    def socket(self) -> Socket:
        return Socket.instance()

    @fixture
    def client(self, app: App) -> FlaskClient:
        return app.test_client

    @fixture
    def socket_client(self, app: App, socket: Socket) -> SocketIOTestClient:
        # https://github.com/miguelgrinberg/Flask-SocketIO/blob/main/test_socketio.py
        return socket.get_test_client()

    @fixture
    def root_dir(self, app: App) -> str:
        return app.root_dir
