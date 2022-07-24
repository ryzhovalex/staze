from staze import View

from .user import User


class UsersIdView(View):
    ROUTE: str = '/users/<id>'

    def get(self, id: int):
        user: User = User.get_first(id=id)
        return {
            'username': user.username,
            'post_ids': [post.id for post in user.posts]
        }
