import json
from types import NoneType
from typing import TYPE_CHECKING, Any, Literal, Sequence
from loguru._handler import Message
from flask import request
from staze.core.app.app_mode_enum import AppModeEnumUnion, RunAppModeEnum

from staze.core.log.log_error import LogError
from staze.core.log.log_snapshot_field_spec_enum import LogSnapshotFieldSpecEnum

if TYPE_CHECKING:
    from staze.core.service.service import Service


class Layer:
    """Layer to operate with logs.
    
    Args:
        path:
            Path to file to save formatted logs to.
        compression (optional):
            Compression format to which log files should be converted.
        rotation (optional):
            Condition indicating wheneve the current logged file should be
            closed and a new one started. 
    """

    def __init__(
                self,
                path: str,
                mode_enum: AppModeEnumUnion,
                service_by_hash: dict,
                compression: str | None = None,
                rotation: str | None = None,
            ) -> None:
        self._path = path
        self._compression = compression
        self._rotation = rotation
        self._service_by_hash = service_by_hash
        self._mode_enum = mode_enum

    def _populate_request_context(self, log: dict) -> None:
        try:
            request.__dict__
        except RuntimeError:
            # Sometimes operations done without request context. In this case -
            # just skip
            return

        log['http.request.method'] = request.method
        log['http.request.headers'] = dict(request.headers)
        log['http.request.mime_type'] = request.mimetype
        log['http.request.body.content'] = request.get_data(as_text=True)

    def _populate_service_context(self, log: dict, service_hash: int) -> None:
        # FIXME:
        #   I haven't found right field to store my service information in ECS,
        #   so here i just store it in arbitrary field.
        service: 'Service' = self._service_by_hash[service_hash]
        log['service.data'] = self._get_service_snapshot(service)

    def _get_service_snapshot(self, service: 'Service') -> dict:
        rules: dict[str, LogSnapshotFieldSpecEnum] = service.LOG_SNAPSHOT_RULES

        def _check_key_against_rules(key: str) -> bool:
            key_type: Literal['public', 'protected', 'private']

            try:
                key = str(key)
            except:
                # Non-convertable keys should be skipped
                return False

            if not key:
                return False

            if key[0] == '_':
                if len(key) == 1:
                    key_type = 'protected'
                elif key[1] == '__':
                    key_type = 'private'
                else:                
                    key_type = 'protected'
            else:
                key_type = 'public'

            rule = rules[key_type]
            if rule is LogSnapshotFieldSpecEnum.ALWAYS:
                return True
            elif (
                    rule in [
                        LogSnapshotFieldSpecEnum.IF_TEST,
                        LogSnapshotFieldSpecEnum.IF_TEST_OR_DEV
                        ]
                    and self._mode_enum is RunAppModeEnum.TEST
                    ):
                return True
            elif (
                    rule in [
                        LogSnapshotFieldSpecEnum.IF_DEV,
                        LogSnapshotFieldSpecEnum.IF_TEST_OR_DEV
                        ]
                    and self._mode_enum is RunAppModeEnum.DEV
                    ):
                return True
            elif (
                rule is LogSnapshotFieldSpecEnum.IF_PROD
                and self._mode_enum is RunAppModeEnum.PROD
                ):
                return True
            else:
                # Also for NEVER enum
                return False

        def _filter_sequence(list_: Sequence) -> list:
            result: list = []
            for x in list_:
                result.append(_filter_value(x))
            return result

        def _filter_value(
                value: Any
                ) -> int | str | float | dict | list | bool | None:
            if type(value) in [int, str, float, bool, NoneType]:
                return value
            elif type(value) in (list, tuple, set):
                return _filter_sequence(value)
            elif type(value) is dict:
                return _filter_dict(value)
            else:
                # Arbitrary object, check for it's __dict__ first
                if hasattr(value, '__dict__'):
                    return _filter_dict(value.__dict__)
                else:
                    if hasattr(value, '__name__'):
                        return _filter_value(value.__name__)
                    else:
                        return _filter_value(hash(value))

        def _filter_dict(dict_: dict) -> dict:
            # Only JSON-compatible types are stored
            result: dict = {}

            for k, v in dict_.items():
                if _check_key_against_rules(k):
                    value = _filter_value(v)
                    if value:
                        result[k] = value

            return result

        return _filter_dict(service.__dict__)

    def _write(self, log: dict) -> None:
        with open(self._path, 'a+') as file:
            json.dump(log, file)
            file.write('\n')

    def format(self, message: Message) -> None:
        raise NotImplementedError(
            'Should be re-implemented at the children class')
