from pytest import fixture
from staze.core.model.model import Model
from staze.core.test.mock import Mock


class CustomModel(Model):
    name: str
    age: int
    tags: set[str]


class CustomModelMock(Mock):
    name: str
    age: int
    tags: set[str]


@fixture
def custom_model_mock() -> CustomModelMock:
    return CustomModelMock(name='Test', age=12, tags={'hero', 'reckless'})


@fixture
def custom_model(custom_model_mock: CustomModelMock) -> CustomModel:
    return CustomModel(
        name=custom_model_mock.name,
        age=custom_model_mock.age,
        tags=custom_model_mock.tags)


class TestModel():
    def test_custom(
            self, custom_model: CustomModel,
            custom_model_mock: CustomModelMock):
        expected_json: dict = {
            'custom': {
                'name': custom_model_mock.name,
                'age': custom_model_mock.age,
                'tags': custom_model_mock.tags
            }
        }

        assert custom_model.name == custom_model_mock.name
        assert custom_model.age == custom_model_mock.age
        assert custom_model.tags == custom_model_mock.tags

        assert custom_model.formatted_name == 'custom'
        assert custom_model.get_api_dict() == expected_json

        json_custom_name: dict = custom_model.get_api_dict('testname')
        assert 'testname' in json_custom_name
