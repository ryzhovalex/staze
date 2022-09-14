from staze import View
from staze.tests.blog.app.user.user_service import UserService

from .user_orm import UserOrm


class UsersIdView(View):
    ROUTE: str = '/users/<id>'

    def get(self, id: int):
        user_orm: UserOrm = UserOrm.get_first(id=id)
        return user_orm.model.api_dict


class UsersServiceLogView(View):
    ROUTE: str = '/users/service/log'

    def get(self):
        UserService.instance().request_log()
        return {'message': 'Request log is done!'}
