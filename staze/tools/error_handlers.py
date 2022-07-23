from staze.core.error.error import Error
from staze.tools.log import raise_error_to_log


def handle_wildcard_error(err: Error):
    raise_error_to_log(err)
    return err.expose(), err.status_code


def handle_wildcard_builtin_error(err: Exception):
    return handle_wildcard_error(Error('; '.join(err.args), 400))
