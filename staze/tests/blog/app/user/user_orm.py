from typing import TYPE_CHECKING
from staze import Database

from staze.tests.blog.app.badge.badge_orm import BadgeOrm
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

from staze.tests.blog.app.user.user import User

if TYPE_CHECKING:
    from staze.tests.blog.app.post.post_orm import PostOrm


class UserOrm(Database.Orm):
    _username = Database.column(Database.string(150))
    _password = Database.column(Database.string(150))
    _post_orms = Database.relationship(
        'PostOrm', backref='user', foreign_keys='[PostOrm._creator_user_id]')

    @classmethod
    def create(
            cls,
            username: str,
            password: str) -> 'UserOrm':
        return cls(
            _username=username,
            _password=generate_password_hash(password))

    def add_post(self, post_orm: 'PostOrm'):
        self._post_orms.append(post_orm)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self._password, password)

    @hybrid_property
    def username(self) -> str:
        return self._username

    @hybrid_property
    def post_ids(self) -> list[int]:
        return [orm.id for orm in self._post_orms]

    @hybrid_property
    def model(self) -> User:
        return User(
            id=self.id,
            type=self.type,
            username=self.username
        )


class AdvancedUserOrm(UserOrm):
    _badge_id = Database.column(
        Database.integer, Database.foreign_key(BadgeOrm._id))

    @classmethod
    def create(
            cls,
            username: str,
            password: str,
            badge_orm: BadgeOrm) -> 'AdvancedUserOrm':
        orm = cls(
            username=username,
            password=generate_password_hash(password))
        badge_orm.add_advanced_user(orm)
        return orm
