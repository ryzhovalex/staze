from staze.core.app.app import App
from staze.core.database.database import Database
from staze.core.service.service import Service
# from flask_admin import Admin as FlaskAdmin
# from flask_admin.contrib.sqla import ModelView


class Admin(Service):
    def __init__(self, config: dict, app: App, database: Database) -> None:
        super().__init__(config)
    #     self._swatch = self.config.get('swatch', 'cerulean')
    #     self._app: App = app
    #     self._db: Database = database
    #     self._app.native_app.config['FLASK_ADMIN_SWATCH'] = self._swatch
    #     self._admin: FlaskAdmin = FlaskAdmin(
    #         self._app.native_app,
    #         name='Admin',
    #         template_mode='bootstrap3'
    #     )

    #     # TMP
    #     from staze.tests.blog.app.user.user_orm import UserOrm
    #     from staze.tests.blog.app.post.post_orm import PostOrm
    #     self._admin.add_view(
    #         ModelView(UserOrm, self._db.native_database.session)
    #         )
    #     self._admin.add_view(
    #         ModelView(PostOrm, self._db.native_database.session)
    #         )
