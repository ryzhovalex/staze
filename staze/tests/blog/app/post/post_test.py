from pytest import fixture
from blog.app.post.post_orm import PostOrm
from staze.core.app.app import App
from staze.core.database.database import Database
from staze.tests.blog.app.user.user_orm import UserOrm


@fixture
def post_orm(self, app: App, db: Database, user_orm: UserOrm) -> PostOrm:
    with app.app_context():
        return PostOrm.create(
            title='My first post',
            content='Some content of mine',
            creator_user_orm=user_orm)
