import os
from staze import Test
from staze.core.app.app import App
from staze.core.assembler.assembler import Assembler
from staze.core.database.database import Database
from flask.testing import FlaskClient
from werkzeug.test import TestResponse
from staze.core.log import log
from staze.core.test.http_client import HttpClient
from staze.tests.blog.app.user.user_service import UserService


# class TestApiUser(Test):
#     def test_get(
#             self,
#             app: App,
#             db: Database,
#             client: FlaskClient,
#             http: HttpClient):
#         with app.app_context():
#             response: TestResponse = http.get('/users/1', 404)


class TestUser(Test):
    def test_photo_path(
            self, assembler_dev: Assembler, app: App, root_dir: str):
        log.debug(assembler_dev.custom_services['user'].config)
        assert \
            assembler_dev.custom_services['user'].config['photo_path'] \
                == os.path.join(root_dir, 'assets/user/photo.png')