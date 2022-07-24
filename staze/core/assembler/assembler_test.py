import os

from pytest import fixture
from staze.core.assembler.assembler import Assembler
from staze.core.assembler.build import Build
from staze.core.app.app_mode_enum import RunAppModeEnum
from staze.core.app.app import App
from staze.core.database.database import Database
from staze.core.log import log
from staze.tests.blog.app.user.user_service import UserService


@fixture
def assembler_dev(
        blog_build: Build, default_host: str, default_port: int,
        blog_root_dir: str):
    return Assembler(
        build=blog_build,
        mode_enum=RunAppModeEnum.DEV,
        host=default_host,
        port=default_port,
        root_dir=os.path.join(os.getcwd(), blog_root_dir))


class TestAssembler():
    def test_build(self, assembler_dev: Assembler):
        app: App = App.instance()
        database: Database = Database.instance()
        user_service: UserService = assembler_dev.custom_services['user']
