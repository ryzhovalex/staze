from staze import View

from .user_orm import UserOrm


class UsersIdView(View):
    ROUTE: str = '/users/<id>'

    def get(self, id: int):
        user_orm: UserOrm = UserOrm.get_first(id=id)
        return {
            'username': user_orm.username,
            'post_ids': user_orm.post_ids
        }
