from typing import TYPE_CHECKING

from staze.core.database.database import Database
from .post_tag_table import PostTagTable
from staze.tests.blog.app.user.user_orm import UserOrm

if TYPE_CHECKING:
    from staze.tests.blog.app.tag.tag_orm import TagOrm


class PostOrm(Database.Orm):
    _title = Database.column(Database.string(150))
    _content = Database.column(Database.text)
    _creator_user_id = Database.column(
        Database.integer, Database.foreign_key(UserOrm._id))
    _tag_orms = Database.relationship(
        'TagOrm',
        secondary=PostTagTable,
        lazy='subquery',
        backref='_post_orms')

    @classmethod
    def create(
            cls,
            title: str,
            content: str,
            creator_user_orm: 'UserOrm') -> 'PostOrm':
        orm = cls(
            _title=title,
            _content=content
        )
        creator_user_orm.add_post(orm)
        return orm

    def add_tag(self, tag_orm: 'TagOrm'):
        self._tag_orms.append(tag_orm)
