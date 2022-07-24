from staze import Test
from staze.core.app.app import App
from staze.core.database.database import Database
from flask.testing import FlaskClient
from werkzeug.test import TestResponse
from staze.core.test.http_client import HttpClient


# class TestApiUser(Test):
#     def test_get(
#             self,
#             app: App,
#             db: Database,
#             client: FlaskClient,
#             http: HttpClient):
#         with app.app_context():
#             response: TestResponse = http.get('/users/1', 404)