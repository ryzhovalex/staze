import os

from pytest import fixture
from staze.core.assembler.assembler import Assembler
from staze.core.assembler.build import Build
from staze.core.app.app_mode_enum import RunAppModeEnum
from staze.core.app.app import App
from staze.core.database.database import Database
from staze.core.log.log import log
from staze.core.test.test import Test
from staze.tests.blog.app.user.user_service import UserService


@fixture
def assembler_test(
        blog_build: Build, default_host: str, default_port: int,
        blog_root_dir: str):
    assembler = Assembler(
        build=blog_build,
        mode_enum=RunAppModeEnum.TEST,
        host=default_host,
        port=default_port,
        root_dir=os.path.join(os.getcwd(), blog_root_dir),
        _is_self_test=True,
        _has_to_recreate_migrations=True
        )
    
    assembler.run(_has_to_run_app=False)

    yield assembler

    assembler.cleanup_all_services()
    assembler.__class__.instances = {}


@fixture
def assembler_dev(
        blog_build: Build, default_host: str, default_port: int,
        blog_root_dir: str):
    assembler = Assembler(
        build=blog_build,
        mode_enum=RunAppModeEnum.DEV,
        host=default_host,
        port=default_port,
        root_dir=os.path.join(os.getcwd(), blog_root_dir),
        _is_self_test=False,
        _has_to_recreate_migrations=True
        )
    
    assembler.run(_has_to_run_app=False)

    yield assembler

    assembler.cleanup_all_services()
    assembler.__class__.instances = {}


@fixture
def assembler_prod(
        blog_build: Build, default_host: str, default_port: int,
        blog_root_dir: str):
    assembler = Assembler(
        build=blog_build,
        mode_enum=RunAppModeEnum.PROD,
        host=default_host,
        port=default_port,
        root_dir=os.path.join(os.getcwd(), blog_root_dir),
        _is_self_test=True,
        _has_to_recreate_migrations=True
        )
    
    assembler.run(_has_to_run_app=False)

    yield assembler

    assembler.cleanup_all_services()
    assembler.__class__.instances = {}

    Assembler.instances = {}


class TestAssembler(Test):
    def test_create_manual(self,
            blog_build: Build, default_host: str, default_port: int,
            blog_root_dir: str):
        assembler = Assembler(
            build=blog_build,
            mode_enum=RunAppModeEnum.TEST,
            host=default_host,
            port=default_port,
            root_dir=os.path.join(os.getcwd(), blog_root_dir))
        
        assert assembler.mode_enum == RunAppModeEnum.TEST

    def test_build(self, assembler_dev: Assembler):
        app: App = App.instance()
        database: Database = Database.instance()
        user_service: UserService = assembler_dev.custom_services['user']
