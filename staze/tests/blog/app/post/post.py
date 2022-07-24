from typing import TYPE_CHECKING

from staze import Database

from blog.app.user.user import User
from .post_tag_table import PostTagTable
from .tag.tag import Tag


class Post(Database.Orm):
    title = Database.column(Database.string(150))
    content = Database.column(Database.text)
    user_id = Database.column(Database.integer, Database.foreign_key(User.id))
    tags = Database.relationship(
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
