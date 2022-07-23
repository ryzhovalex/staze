from ctypes import c_size_t
from dataclasses import dataclass
from typing import ClassVar
from pytest import fixture
from staze.core.ie.ie import Ie
from staze.core.test.mock import Mock


@dataclass
class CustomIe(Ie):
    name: str
    age: int
    tags: set[str]


@dataclass
class CustomIeMock(Mock):
    name: str
    age: int
    tags: set[str]


@fixture
def custom_ie_mock() -> CustomIeMock:
    return CustomIeMock(name='Test', age=12, tags={'hero', 'reckless'})


@fixture
def custom_ie(custom_ie_mock: CustomIeMock) -> CustomIe:
    return CustomIe(
        name=custom_ie_mock.name,
        age=custom_ie_mock.age,
        tags=custom_ie_mock.tags)


class TestIe():
    def test_custom(self, custom_ie: CustomIe, custom_ie_mock: CustomIeMock):
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
