from staze.core.error.error import Error
from typing import Callable

from staze.core.app.app import App
from staze.core.log import log, raise_error_to_log
from staze.core.error.error import Error
from staze.core.service.service import Service
from warepy import Singleton


class ErrorHandler(Singleton):
    def __init__(
            self,
            app: App,
            default_error_handler: Callable | None = None,
            default_builtin_error_handler: Callable | None = None) -> None:
        self.default_error_handler: Callable
        self.default_builtin_error_handler: Callable

        if isinstance(default_error_handler, Callable):
            self.default_error_handler = default_error_handler
        else:
            self.default_error_handler = self._handle_error_default

        if isinstance(default_builtin_error_handler, Callable):
            self.default_builtin_error_handler = default_builtin_error_handler
        else:
            self.default_builtin_error_handler = \
                self._handle_builtin_error_default

        # Register main handler function
        app.register_error(Exception, self.handle_error)
        
    def handle_error(self, err: Exception):
        if isinstance(err, Error):
            if err.SHOULD_BE_LOGGED:
                raise_error_to_log(err)
            if err.HANDLER_FUNCTION:
                return err.HANDLER_FUNCTION(err)
            else:
                # Use default
                return self.default_error_handler(err)
        else:
            # Log builtin exceptions in any case
            raise_error_to_log(err)
            return self.default_builtin_error_handler(err)

    def _handle_error_default(self, err: Error):
        return err.expose(), err.status_code

    def _handle_builtin_error_default(self, err: Exception):
        return self._handle_error_default(
            Error('; '.join(err.args), 400))
