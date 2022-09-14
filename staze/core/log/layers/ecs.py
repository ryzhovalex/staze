import json
from datetime import datetime, timezone
from loguru._handler import Message
from staze.core.log.layers.layer import Layer
from staze.core.log.log_error import LogError


class Ecs(Layer):
    def format(self, message: Message):
        result: dict = {}
        record = message.record

        labels: dict = {}

        self._populate_request_context(result)
        
        client_ip: str | None = None
        url_full: str | None = None
        url_path: str | None = None
        url_port: str | None = None
        url_query: str | None = None

        http_request_mime_type: str | None = None
        http_request_method: str | None = None
        http_request_headers: dict | None = None
        http_request_body_content: str | None = None

        http_response_status_code: int | None = None
        http_response_headers: dict | None = None
        http_response_mime_type: str | None = None
        http_response_body_content: str | None = None

        error_type: str | None = None
        error_message: str | None = None
        error_code: int | None = None

        # Extra dictionary transformed to ECS labels shouldn't contain nested
        # objects in values as ECS restricts
        # https://www.elastic.co/guide/en/ecs/current/ecs-base.html
        for k, v in record['extra'].items():
            # Client information should be stored separately
            match k:
                case 'service_hash':
                    service_hash = v
                    if type(service_hash) is not int:
                        raise LogError(
                            'Service hash should have type int,'
                            f' got {type(service_hash)} instead'
                            )
                    self._populate_service_context(result, service_hash)
                    # Write service hash to labels anyway
                    labels[k] = v
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
                case 'http_response_headers':
                    if type(v) is not dict:
                        raise LogError(
                            'Value of response headers should be dict,'
                            f' got {type(v)} instead'
                        )
                    http_response_headers = v
                case 'http_response_mime_type':
                    if type(v) is not str:
                        raise LogError(
                            'Value of response mimetype should be str,'
                            f' got {type(v)} instead'
                        )
                    http_response_mime_type = v
                case 'http_response_body_content':
                    if type(v) is not str:
                        raise LogError(
                            'Value of response body content should be str,'
                            f' got {type(v)} instead'
                        )
                    http_response_body_content = v
                case 'http_request_headers':
                    if type(v) is not dict:
                        raise LogError(
                            'Value of request headers should be dict,'
                            f' got {type(v)} instead'
                        )
                    http_request_headers = v
                case 'http_request_body_content':
                    if type(v) is not str:
                        raise LogError(
                            'Value of request body content should be str,'
                            f' got {type(v)} instead'
                        )
                    http_request_body_content = v
                case 'http_request_mime_type':
                    if type(v) is not str:
                        raise LogError(
                            'Value of request mimetype should be str,'
                            f' got {type(v)} instead'
                        )
                    http_request_mime_type = v
                case _:
                    if type(k) is not str:
                        raise LogError(f'Key {k} of extra field should be str')
                    if type(v) not in [str, int, float]:
                        raise LogError(
                            f'Value {v} of extra field should be str, int or'
                            ' float'
                            )
                    labels[k] = v

        # Since loguru correctly sets up timezone for every datetime emitted,
        # there is not problem of getting timestamp directly - utc timestamp
        # will be returned
        result['@timestamp'] = record['time'].timestamp()
        result['labels'] = labels
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

        if error_type:
            result['error.type'] = error_type
        if error_message:
            result['error.message'] = error_message
        if error_code:
            result['error.code'] = error_code

        if http_request_method:
            result['http.request.method'] = http_request_method
        if http_request_headers:
            result['http.request.headers'] = http_request_headers
        if http_request_mime_type:
            result['http.request.mime_type'] = http_request_mime_type
        if http_request_body_content:
            result['http.request.body.content'] = http_request_body_content

        if http_response_status_code:
            result['http.response.status_code'] = http_response_status_code
        if http_response_headers:
            result['http.response.headers'] = http_response_headers
        if http_response_mime_type:
            result['http.response.mime_type'] = http_response_mime_type
        if http_response_body_content:
            result['http.response.body.content'] = http_response_body_content

        result['ecs.version'] = '8.4'

        self._write(result)
