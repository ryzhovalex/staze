from typing import Callable
from pytest import fixture
from flask_socketio import SocketIOTestClient
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from staze.core.app.app import App
from staze.core import validation, parsing
from staze.core.database.database import Database
from staze.core.socket.socket import Socket


class Test:
    @fixture
    def http(self, app: App, client: FlaskClient) -> Callable:
        def inner(
                request: str,
                asserted_status_code: int,
                **request_kwargs) -> TestResponse:
            response: TestResponse
            test_client_method: Callable
            method: str
            url: str

            validation.validate(request, str)
            validation.validate(asserted_status_code, int)

            # Request example: 'get /users/1'
            method, url = request.split(' ')

            # Also can accept uppercase 'GET ...'
            method = method.lower()

            match method:
                case 'get':
                    test_client_method = app.test_client.get
                case 'post':
                    test_client_method = app.test_client.post
                case 'put':
                    test_client_method = app.test_client.put
                case 'patch':
                    test_client_method = app.test_client.patch
                case 'delete':
                    test_client_method = app.test_client.delete
                case _:
                    raise ValueError(f'Method {method} is not supported')

            response =  test_client_method(url, **request_kwargs)

            assert response.status_code == asserted_status_code

            return response

        return inner

    @fixture
    def app(self):
        app: App = App.instance()
        yield app

    @fixture
    def database(self, app: App):
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
