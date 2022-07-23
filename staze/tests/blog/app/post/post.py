from typing import TYPE_CHECKING

from staze import orm

from blog.app.user.user import User
from .post_tag_table import PostTagTable
from .tag.tag import Tag


class Post(orm.Mapper):
    title = orm.column(orm.string(150))
    content = orm.column(orm.text)
    user_id = orm.column(orm.integer, orm.foreign_key(User.id))
    tags = orm.relationship(
        'Tag', secondary=PostTagTable, lazy='subquery', backref='posts')

    @classmethod
    def create(
            cls,
            title: str,
            user: User,
            content: str = '',
            tags: list[Tag] = []) -> 'Post':
        post: Post = cls(
            title=title,
            content=content)

        post.set_user(user)
        for tag in tags:
            post.set_tag(tag)

        return post

    def set_user(self, user: User) -> None:
        user.posts.append(self)

    def set_tag(self, tag: Tag) ->  None:
        self.tags.append(tag)
