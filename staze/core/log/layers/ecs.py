import json
from datetime import datetime, timezone
from loguru._handler import Message
from staze.core.log.layers.layer import Layer
from staze.core.log.log_error import LogError


class Ecs(Layer):
    def format(self, message: Message):
        result: dict = {}
        record = message.record

        record_extra: dict = {}

        self._populate_with_request_context(record_extra)
        
        client_ip: str | None = None
        url_full: str | None = None
        url_path: str | None = None
        url_port: str | None = None
        url_query: str | None = None
        http_request_method: str | None = None
        http_response_status_code: int | None = None

        error_type: str | None = None
        error_message: str | None = None
        error_code: int | None = None

        # Extra dictionary transformed to ECS labels shouldn't contain nested
        # objects in values as ECS restricts
        # https://www.elastic.co/guide/en/ecs/current/ecs-base.html
        for k, v in record['extra'].items():
            if type(k) is not str:
                raise LogError(f'Key {k} of extra field should be str')
            if type(v) not in [str, int, float]:
                raise LogError(
                    f'Value {v} of extra field should be str, int or float'
                    )

            # Client information should be stored separately
            match k:
                case 'client_ip':
                    if type(v) is not str:
                        raise LogError(
                            'Value of client ip should be string,'
                            f' got {type(v)} instead'
                        )
                    client_ip = v
                case 'url_full':
                    if type(v) is not str:
                        raise LogError(
                            'Value of full url should be string,'
                            f' got {type(v)} instead'
                        )
                    url_full = v
                case 'url_path':
                    if type(v) is not str:
                        raise LogError(
                            'Value of url path should be string,'
                            f' got {type(v)} instead'
                        )
                    url_path = v
                case 'url_port':
                    if type(v) is not str:
                        raise LogError(
                            'Value of url port should be string,'
                            f' got {type(v)} instead'
                        )
                    url_port = v
                case 'url_query':
                    if type(v) is not str:
                        raise LogError(
                            'Value of url query should be string,'
                            f' got {type(v)} instead'
                        )
                    url_query = v
                case 'http_request_method':
                    if type(v) is not str:
                        raise LogError(
                            'Value of http request method should be string,'
                            f' got {type(v)} instead'
                        )
                    http_request_method = v
                case 'http_response_status_code':
                    if type(v) is not int:
                        raise LogError(
                            'Value of http response status code should be int,'
                            f' got {type(v)} instead'
                        )
                    http_response_status_code = v
                case 'error_type':
                    if type(v) is not str:
                        raise LogError(
                            'Value of error type should be str,'
                            f' got {type(v)} instead'
                        )
                    error_type = v
                case 'error_message':
                    if type(v) is not str:
                        raise LogError(
                            'Value of error message should be str,'
                            f' got {type(v)} instead'
                        )
                    error_message = v
                case 'error_code':
                    if type(v) is not int:
                        raise LogError(
                            'Value of error code should be int,'
                            f' got {type(v)} instead'
                        )
                    error_code = v
                case _:
                    record_extra[k] = v

        # Since loguru correctly sets up timezone for every datetime emitted,
        # there is not problem of getting timestamp directly - utc timestamp
        # will be returned
        result['@timestamp'] = record['time'].timestamp()
        result['labels'] = record_extra
        result['message'] = record['message']
        result['log.file.path'] = record['file'].path
        result['log.level'] = record['level'].name
        result['log.origin.file.line'] = record['line']
        result['log.origin.file.name'] = record['name']
        result['log.origin.function'] = record['function']
        if client_ip:
            result['client.ip'] = client_ip
        if url_full:
            result['url.full'] = url_full
        if url_path:
            result['url.path'] = url_path
        if url_port:
            result['url.query'] = url_query
        if http_request_method:
            result['http.request.method'] = http_request_method
        if http_response_status_code:
            result['http.response.status_code'] = http_response_status_code
        if error_type:
            result['error.type'] = error_type
        if error_message:
            result['error.message'] = error_message
        if error_code:
            result['error.code'] = error_code

        self._write(result)
