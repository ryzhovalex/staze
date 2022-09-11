import sys
from io import StringIO 

from pytest import fixture
from staze.core.test.test import Test
from staze.core.assembler.build import Build
from staze.core.validation import validate_re
from staze.core.cli.cli import Cli
from staze.core.log import log


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


class TestCliExecute(Test):
    def test_default(self):
        cli = Cli()
        with Capturing() as out:
            try:
                cli.execute(['staze', 'version'])
            except SystemExit:
                pass
            else:
                raise AssertionError('')

        assert len(out) == 1
        validate_re(out[0], r'Staze \d+\.\d+\.\d+')

    def test_dev(self, blog_root_dir: str, blog_build: Build):
        cli = Cli(root_dir=blog_root_dir)
        with Capturing() as out:
            cli.execute(['staze', 'dev'])
            
