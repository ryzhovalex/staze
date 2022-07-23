from pytest import fixture
from flask_socketio import SocketIOTestClient
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from staze.core.app.app import Staze
from staze.core import validation, parsing
from staze.core.db.db import Db
from staze.core.sock.socket import Socket
from staze.tools.get_root_dir import get_root_dir


class Test:
    # @fixture
    # def request(self, app: Staze, client: FlaskClient) -> TestResponse:
    #     def inner(request: str, asserted_status_code: int):
    #         response: TestResponse
    #         method: str
    #         url: str

    #         validation.validate

    #         # Request example: 'get /users/1'
    #         method, url = request.split(' ')

    #         # Also can accept uppercase 'GET ...'
    #         method = method.lower()

    #         match method:
    #             case 'get':
    #                 response = app.test_client().get()
    #             case

    #     return inner

    @fixture
    def app(self):
        app: Staze = Staze.instance()
        yield app

    @fixture
    def db(self, app: Staze):
        db: Db = Db.instance()

        with app.app_context():
            db.drop_all()
            db.create_all()

        yield db

        with app.app_context():
            db.drop_all()

    @fixture
    def socket(self) -> Socket:
        return Socket.instance()

    @fixture
    def client(self, app: Staze) -> FlaskClient:
        return app.test_client()

    @fixture
    def socket_client(self, app: Staze, socket: Socket) -> SocketIOTestClient:
        # https://github.com/miguelgrinberg/Flask-SocketIO/blob/main/test_socketio.py
        return socket.get_test_client()

    @fixture
    def root_dir(self) -> str:
        return get_root_dir()
