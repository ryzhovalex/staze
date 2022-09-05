from pytest import fixture
from staze.core.model.model import Model
from staze.core.test.mock import Mock
from staze.core.log import log


class CustomModel(Model):
    name: str
    age: int
    tags: set[str]


class NestingCustomModel(Model):
    custom_model: CustomModel


class NestingListCustomModel(Model):
    custom_models: list[CustomModel]


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
        log.debug(expected_json)

        assert custom_model.name == custom_model_mock.name
        assert custom_model.age == custom_model_mock.age
        assert custom_model.tags == custom_model_mock.tags

        assert custom_model.formatted_name == 'custom'
        assert custom_model.get_api_dict() == expected_json

        json_custom_name: dict = custom_model.get_api_dict('testname')
        assert 'testname' in json_custom_name

    def test_nesting_custom(
        self, custom_model_mock: CustomModelMock, custom_model: CustomModel
    ):
        expected: dict = {
            'nesting_custom': {
                'custom': {
                    'name': custom_model_mock.name,
                    'age': custom_model_mock.age,
                    'tags': custom_model_mock.tags
                }
            }
        }

        target: NestingCustomModel = NestingCustomModel(
            custom_model=custom_model
        )

        assert target.formatted_name == 'nesting_custom'
        assert target.api_dict == expected
        a = [{'t': 1}, {'b': 2}]

    def test_nesting_list_custom(self):
        expected: dict = {
            'nesting_list_custom': {
                'custom_models': [
                    {
                        'custom': {
                            'name': '1',
                            'age': 1,
                            'tags': {'1'}
                        }
                    },
                    {
                        'custom': {
                            'name': '2',
                            'age': 2,
                            'tags': {'1', '2'}
                        }
                    },
                    {
                        'custom': {
                            'name': '3',
                            'age': 3,
                            'tags': {'1', '2', '3'}
                        }
                    }
                ]
            }
        }

        target = NestingListCustomModel(
            custom_models=[
                CustomModel(name='1', age=1, tags={'1'}),
                CustomModel(name='2', age=2, tags={'1', '2'}),
                CustomModel(name='3', age=3, tags={'1', '2', '3'})
            ]
        )

        assert target.api_dict == expected
