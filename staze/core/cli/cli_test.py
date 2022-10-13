import sys
from io import StringIO

from pytest import fixture
from staze.core.app.app_mode_enum import RunAppModeEnum
from staze.core.constants import DEFAULT_HOST, DEFAULT_PORT
from staze.core.assembler.assembler import Assembler
from staze.core.assembler.assembler_error import (
    NoDefinedExecutablesExecAssemblerError,
    NoExecutableWithSuchNameExecAssemblerError)
from staze.core.assembler.build import Build
from staze.core.cli.cli import Cli
from staze.core.cli.cli_error import (BindStringParsingCliError, RedundantFlagCliError,
                                      RedundantValueCliError,
                                      RepeatingArgCliError,
                                      UncompatibleArgsCliError)
from staze.core.database.database import Database
from staze.core.log.log import log
from staze.core.test.test import Test
from staze.core.validation import validate_re
from staze.tests.blog.app.user.user_orm import UserOrm
from staze.tests.blog.build import add_user


# FIXME: Remove and import from warepy as it is introduced there
class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout


@fixture
def cli_blog(blog_root_dir: str, blog_build: Build):
    yield Cli(root_dir=blog_root_dir, build=blog_build)

    try:
        assembler: Assembler = Assembler.instance()
    except TypeError:
        # Test of errors may not call assembler creation, so here on teardown
        # error of unexistent assembler may be thrown, so ignore it
        return
    else:
        assembler.cleanup_all_services()
        assembler.__class__.instances = {}


class TestCliExecute:
    def test_version(self, cli_blog: Cli):
        with Capturing() as out:
            try:
                cli_blog.execute(['staze', 'version'], _is_self_test=True)
            except SystemExit:
                pass
            else:
                raise AssertionError('')

        # Capturing.out should be tested only outside of "with" block
        # FIXME: len(out) = 0
        # assert len(out) == 1
        # validate_re(out[0], r'Staze \d+\.\d+\.\d+')

    def test_version_redundant_flag(self, cli_blog: Cli):
        try:
            cli_blog.execute(
                ['staze', 'version', '-b', '0.0.0.0'],
                _is_self_test=True
                )
        except (RedundantFlagCliError, SystemExit):
            return
        else:
            raise AssertionError(
                'Executing "staze version" with additional flags should'
                ' result in error'
            )

    def test_version_redundant_value(self, cli_blog: Cli):
        try:
            cli_blog.execute(['staze', 'version', 'hello'], _is_self_test=True)
        except (RedundantValueCliError, SystemExit):
            return
        else:
            raise AssertionError(
                'Executing "staze version" with additional values should'
                ' result in error'
            )

    def test_test(self, cli_blog: Cli):
        assembler: Assembler = cli_blog.execute(
            ['staze', 'test'], has_to_run_assembler=False, _is_self_test=True)
        assert assembler.mode_enum.value == 'test'

    def test_dev(self, cli_blog: Cli):
        assembler: Assembler = cli_blog.execute(
            ['staze', 'dev'], has_to_run_assembler=False, _is_self_test=True)
        assert assembler.mode_enum.value == 'dev'

    def test_prod(self, cli_blog: Cli):
        assembler: Assembler = cli_blog.execute(
            ['staze', 'prod'], has_to_run_assembler=False, _is_self_test=True)
        assert assembler.mode_enum.value == 'prod'

    def test_host_port(self, cli_blog: Cli):
        assembler: Assembler = cli_blog.execute(
            ['staze', 'prod', '-b', '0.0.0.0:6000'],
            has_to_run_assembler=False,
            _is_self_test=True
        )

        # FIXME:
        #   In strange way app always receives default port and host in this
        #   test environment, and i don't know why.
        #   It happens for both "prod" and "dev" modes.
        #   But in assembler this values are OK. But assembler.app.host and 
        #   assembler.app.port are set to defaults...
        #
        assert assembler.host == '0.0.0.0'
        assert assembler.port == 6000
        assert assembler.mode_enum.value == 'prod'

    def test_execute(self, cli_blog: Cli):
        assembler: Assembler = cli_blog.execute(
            ['staze', 'exec', 'add_user'],
            has_to_run_assembler=False,
            _has_to_recreate_migrations=True,
            _is_self_test=True
        )
        assert assembler.executables_to_execute == ['add_user']

        assembler.run()

        with assembler.app.app_context():
            user_orm: UserOrm = UserOrm.get_first()
            user_orm.check_password('helloworld')

    def test_execute_on_run_mode(self, cli_blog: Cli):
        assembler: Assembler = cli_blog.execute(
            ['staze', 'dev', '-x', 'add_user'],
            has_to_run_assembler=False,
            _has_to_recreate_migrations=True,
            _is_self_test=True
        )
        assert assembler.executables_to_execute == ['add_user']

        assembler.run(_has_to_run_app=False)

        with assembler.app.app_context():
            user_orm: UserOrm = UserOrm.get_first()
            user_orm.check_password('helloworld')

    def test_execute_on_db_init_mode(self, cli_blog: Cli):
        try:
            assembler: Assembler = cli_blog.execute(
                ['staze', 'init', '-x', 'add_user'],
                has_to_run_assembler=False,
                _is_self_test=True
            )
        except UncompatibleArgsCliError:
            pass
        else:
            raise AssertionError(
                'Execution on db init mode should result in'
                ' UncompatibleArgsCliError'
            )

    def test_executable_repeating(self, cli_blog: Cli):
        try:
            assembler: Assembler = cli_blog.execute(
                ['staze', 'dev', '-x', 'add_user', '-x', 'add_user'],
                has_to_run_assembler=False,
                _is_self_test=True
            )
        except RepeatingArgCliError:
            pass
        else:
            raise AssertionError(
                'Repeating -x flag should result in RepeatingArgCliError'
            )

    def test_exec_wrong_name(self, cli_blog: Cli):
        assembler: Assembler = cli_blog.execute(
            ['staze', 'exec', 'add_user123'],
            has_to_run_assembler=False,
            _is_self_test=True
        )

        try:
            assembler.run(_has_to_run_app=False)
        except NoExecutableWithSuchNameExecAssemblerError: 
            pass
        else:
            raise AssertionError(
                'Calling assembler with wrong executable name should result'
                ' in ExecutableAssemblerError'
            )

    def test_bind_two_colons(self, cli_blog: Cli):
        try:
            cli_blog.execute(
                ['staze', 'prod', '-b', '0.0.0.0:5233:123'],
                _is_self_test=True
                )
        except (BindStringParsingCliError):
            return
        else:
            raise AssertionError(
                "Calling --bind with several colons should be prohibited"
            )

    def test_bind_colon_plus_port(self, cli_blog: Cli):
        assembler: Assembler = cli_blog.execute(
            ["staze", "prod", "-b", ":3000"],
            has_to_run_assembler=False,
            _is_self_test=True
        )

        assert assembler.host == DEFAULT_HOST
        assert assembler.port == 3000
        assert assembler.mode_enum.value == "prod"
