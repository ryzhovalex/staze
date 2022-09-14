import json
from loguru._handler import Message
from flask import request


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
                compression: str | None = None,
                rotation: str | None = None
            ) -> None:
        self._path = path
        self._compression = compression
        self._rotation = rotation

    def _populate_with_request_context(self, log: dict) -> None:
        # {'method': 'GET', 'scheme': 'http', 'server': ('127.0.0.1', 5000), 'root_path': '', 'path': '/favicon.ico', 'query_string': b'', 'headers': EnvironHeaders([('Host', '127.0.0.1:5000'), ('Connection', 'keep-alive'), ('Sec-Ch-Ua', '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"'), ('Sec-Ch-Ua-Mobile', '?0'), ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'), ('Sec-Ch-Ua-Platform', '"Linux"'), ('Accept', 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'), ('Sec-Fetch-Site', 'same-origin'), ('Sec-Fetch-Mode', 'no-cors'), ('Sec-Fetch-Dest', 'image'), ('Referer', 'http://127.0.0.1:5000/users/1'), ('Accept-Encoding', 'gzip, deflate, br'), ('Accept-Language', 'en-US,en-RU;q=0.9,en;q=0.8,ru-RU;q=0.7,ru;q=0.6,en-GB;q=0.5')]), 'remote_addr': '127.0.0.1', 'environ': {'wsgi.version': (1, 0), 'wsgi.url_scheme': 'http', 'wsgi.input': <_io.BufferedReader name=6>, 'wsgi.errors': <_io.TextIOWrapper name='<stderr>' mode='w' encoding='utf-8'>, 'wsgi.multithread': True, 'wsgi.multiprocess': False, 'wsgi.run_once': False, 'werkzeug.socket': <socket.socket fd=6, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 5000), raddr=('127.0.0.1', 41424)>, 'SERVER_SOFTWARE': 'Werkzeug/2.1.2', 'REQUEST_METHOD': 'GET', 'SCRIPT_NAME': '', 'PATH_INFO': '/favicon.ico', 'QUERY_STRING': '', 'REQUEST_URI': '/favicon.ico', 'RAW_URI': '/favicon.ico', 'REMOTE_ADDR': '127.0.0.1', 'REMOTE_PORT': 41424, 'SERVER_NAME': '127.0.0.1', 'SERVER_PORT': '5000', 'SERVER_PROTOCOL': 'HTTP/1.1', 'HTTP_HOST': '127.0.0.1:5000', 'HTTP_CONNECTION': 'keep-alive', 'HTTP_SEC_CH_UA': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"', 'HTTP_SEC_CH_UA_MOBILE': '?0', 'HTTP_USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36', 'HTTP_SEC_CH_UA_PLATFORM': '"Linux"', 'HTTP_ACCEPT': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8', 'HTTP_SEC_FETCH_SITE': 'same-origin', 'HTTP_SEC_FETCH_MODE': 'no-cors', 'HTTP_SEC_FETCH_DEST': 'image', 'HTTP_REFERER': 'http://127.0.0.1:5000/users/1', 'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br', 'HTTP_ACCEPT_LANGUAGE': 'en-US,en-RU;q=0.9,en;q=0.8,ru-RU;q=0.7,ru;q=0.6,en-GB;q=0.5', 'werkzeug.request': <Request 'http://127.0.0.1:5000/favicon.ico' [GET]>, 'flask.app': <Flask 'staze.core.app.app'>}, 'shallow': False, 'routing_exception': <NotFound '404: Not Found'>, 'host': '127.0.0.1:5000', 'url': 'http://127.0.0.1:5000/favicon.ico'}
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

    def _write(self, log: dict) -> None:
        with open(self._path, 'a+') as file:
            json.dump(log, file)
            file.write('\n')

    def format(self, message: Message) -> None:
        raise NotImplementedError(
            'Should be re-implemented at the children class')
