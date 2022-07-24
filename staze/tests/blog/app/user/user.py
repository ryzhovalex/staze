from typing import TYPE_CHECKING
from staze import Database

from blog.app.badge.badge import Badge
from werkzeug.security import generate_password_hash, check_password_hash

if TYPE_CHECKING:
    from blog.app.post.post import Post


class User(Database.Orm):
    type = Database.column(Database.string(50))
    username = Database.column(Database.string(150))
    password = Database.column(Database.string(150))
    posts = Database.relationship(
        'Post', backref='user', foreign_keys='[Post.user_id]')

    @classmethod
    def create(
            cls,
            username: str,
            password: str,
            posts: list['Post'] = []) -> 'User':
        return cls(
            username=username,
            password=generate_password_hash(password),
            posts=posts)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)


class AdvancedUser(User):
    badge_id = Database.column(Database.integer, Database.foreign_key(Badge.id))

    @classmethod
    def create(
            cls,
            username: str,
            password: str,
            posts: list['Post'] = [],
            badge: Badge | None = None) -> 'AdvancedUser':
        user: AdvancedUser = cls(
            username=username,
            password=generate_password_hash(password),
            posts=posts)
        if badge:
            user.set_badge(badge)
        return user

    def set_badge(self, badge: Badge):
        badge.advanced_users.append(self)
