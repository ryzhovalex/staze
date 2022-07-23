from ctypes import c_size_t
from dataclasses import dataclass
from typing import ClassVar
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
def custom_ie_mock() -> CustomModelMock:
    return CustomModelMock(name='Test', age=12, tags={'hero', 'reckless'})


@fixture
def custom_ie(custom_ie_mock: CustomModelMock) -> CustomModel:
    return CustomModel(
        name=custom_ie_mock.name,
        age=custom_ie_mock.age,
        tags=custom_ie_mock.tags)


class TestModel():
    def test_custom(self, custom_ie: CustomModel, custom_ie_mock: CustomModelMock):
        expected_json: dict = {
            'custom': {
                'name': custom_ie_mock.name,
                'age': custom_ie_mock.age,
                'tags': custom_ie_mock.tags
            }
        }

        assert custom_ie.name == custom_ie_mock.name
        assert custom_ie.age == custom_ie_mock.age
        assert custom_ie.tags == custom_ie_mock.tags

        assert custom_ie.formatted_name == 'custom'
        assert custom_ie.get_json() == expected_json
        
        # Validate self through class method
        custom_ie.validate(custom_ie.get_json())

        json_custom_name: dict = custom_ie.get_json('testname')
        assert 'testname' in json_custom_name
