import sys
from io import StringIO 

from pytest import fixture
from staze.core.app.app_mode_enum import RunAppModeEnum
from staze.core.test.test import Test
from staze.core.assembler.build import Build
from staze.core.validation import validate_re
from staze.core.cli.cli import Cli
from staze.core.log import log
from staze.core.assembler.assembler import Assembler


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
def cli() -> Cli:
    return Cli()


@fixture
def cli_blog(blog_root_dir: str, blog_build: Build):
    yield Cli(root_dir=blog_root_dir, build=blog_build)
    assembler: Assembler = Assembler.instance()
    assembler.cleanup_all_services()
    assembler.__class__.instances = {}


class TestCliExecute(Test):
    def test_default(self, cli: Cli):
        with Capturing() as out:
            try:
                cli.execute(['staze', 'version'])
            except SystemExit:
                pass
            else:
                raise AssertionError('')
        assert len(out) == 1
        validate_re(out[0], r'Staze \d+\.\d+\.\d+')

    def test_test(self, cli_blog: Cli):
        assembler: Assembler = cli_blog.execute(
            ['staze', 'test'], has_to_run_app=False)
        assert assembler.mode_enum.value == 'test'

    def test_dev(self, cli_blog: Cli):
        assembler: Assembler = cli_blog.execute(
            ['staze', 'dev'], has_to_run_app=False)
        assert assembler.mode_enum.value == 'dev'

    def test_prod(self, cli_blog: Cli):
        assembler: Assembler = cli_blog.execute(
            ['staze', 'prod'], has_to_run_app=False)
        assert assembler.mode_enum.value == 'prod'

    def test_host_port(self):
        # assembler: Assembler = cli_blog.execute(
        #     ['staze', 'dev', '-h', '0.0.0.0', '-p', '6000'], has_to_run_app=False)
        # assert assembler.mode_enum.value == 'dev'
        # assert assembler.app.host == '0.0.0.0'
        # assert assembler.app.port == 6000
        from staze.core.app.app import App
        App.instance().__class__.instances = {}
        app = App(
            mode_enum=RunAppModeEnum.DEV,
            host='0.0.0.0',
            port=6000,
            config={'root_dir': 'staze/tests/blog'},
        )
        log.debug(app.host)
        assert False
