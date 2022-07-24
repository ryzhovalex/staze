import os
import sys

from pytest import fixture
from staze import Build

from staze.tests.blog.build import build as _blog_build
from staze.core.assembler.assembler_test import assembler_dev
from staze.core.log import log


@fixture
def blog_build() -> Build:
    build = _blog_build
    build.config_dir = './configs'

    return build


@fixture
def default_host() -> str:
    return '127.0.0.1'


@fixture
def default_port() -> int:
    return 6000


@fixture
def blog_root_dir() -> str:
    return 'staze/tests/blog'
