from pytest import fixture
from staze.core.test.http_client import HttpClient
from staze.core.test.test import Test
from staze.core.app.app import App
from staze.core.database.database import Database
from staze.tests.blog.app.user.user import User
from staze.tests.blog.app.user.user_orm import UserOrm
from staze.core.parsing import parse, parse_key


@fixture
def user_orm(app: App, db: Database) -> UserOrm:
    with app.app_context():
        return UserOrm.create(username='max', password='helloworld')


class TestApiUsersId(Test):
    def test_get(
            self, app: App, db: Database, http: HttpClient, user_orm: UserOrm):
        with app.app_context():
            db.refpush(user_orm)
            response = http.get('/users/1', 200)
            json: dict = parse(response.json, dict)
            User(**json['user'])
