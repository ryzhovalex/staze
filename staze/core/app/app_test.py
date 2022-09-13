from pytest import fixture

from staze.core.app.app import App


@fixture
def app():
    app: App = App.instance()
    yield app
