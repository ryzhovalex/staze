import os
from pytest import fixture
from staze.core.test.test import Test
from staze.core.app.app import App
from staze.core.assembler.assembler import Assembler
from staze.core.database.database import Database
from flask.testing import FlaskClient
from werkzeug.test import TestResponse
from staze.core.log.log import log
from staze.core.test.http_client import HttpClient
from staze.tests.blog.app.user.user_orm import UserOrm
from staze.tests.blog.app.user.user_service import UserService


@fixture
def user_orm(assembler_dev: Assembler) -> UserOrm:
    with assembler_dev.app.app_context():
        return UserOrm.create(username='Mark', password='helloworld')


class TestApiUser:
    def test_get(
            self,
            user_orm: UserOrm,
            ):
        assembler: Assembler = Assembler.instance()
        with assembler.app.app_context():
            assembler.database.refpush(user_orm)
            response: TestResponse = assembler.app.test_client.get(
                '/users/1'
            )


class TestUserService:
    def test_config_mode_test(self, assembler_test: Assembler):
        assert \
            assembler_test.custom_services['user'].config['config_mode'] \
                == 'test'

    def test_config_mode_dev(self, assembler_dev: Assembler):
        assert \
            assembler_dev.custom_services['user'].config['config_mode'] \
                == 'dev'

    def test_config_mode_prod(self, assembler_prod: Assembler):
        assert \
            assembler_prod.custom_services['user'].config['config_mode'] \
                == 'prod'

    def test_photo_path(
            self, assembler_dev: Assembler, app: App, root_dir: str):
        assert \
            assembler_dev.custom_services['user'].config['photo_path'] \
                == os.path.join(root_dir, 'assets/user/photo.png')


class TestUserOrm(Test):
    def test_create(self, app: App, db: Database, user_orm: UserOrm):
        with app.app_context():
            db.refpush(user_orm)
            assert user_orm.username == 'Mark'
            assert user_orm.check_password('helloworld')
