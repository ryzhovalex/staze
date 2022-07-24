# NOTE: It's extremely important to not set return typehint in decorators with wraps,
# if you want to save your wrapped function's docstring (occurred in VsCode's Pylance Python Language Server).
# BUT, you should set return type Callable in decorators with arguments, or interpreters like PyRights will bind
# decorated functions to Unknown return type.
from functools import wraps
from typing import Callable

from warepy import format_message
from staze.core.log import log
from flask import session, redirect, url_for


def login_required(
    endpoint_if_not_logged: str, 
    allowed_types: list[str] | None = None, 
    endpoint_if_not_allowed: str | None = None
) -> Callable:
    """Check if user logged in before giving access to wrapped view.
    
    If user is not logged in, redirect him to the login page.
    If user doesn't have access to the view (i.e. his type is not in `allowed_types`), redirect him to backup page.

    Login checked against `flask.session` object with key specified under argument `user_id_session_key`.
    ```py
        session = {
            "user": {
                "username": USERNAME,  # To display during errors, etc.
                "type": USER_TYPE,  # User type to check against argument `allowed_types`.
                # ... another restriction-free fields.
            }
            # ... another session fields.
        }
    ```

    Args:
        endpoint_if_not_logged: 
            Endpoint to redirect to if user is not logged in.
        allowed_types: 
            Types of users that should have access to the view. Defaults to None, i.e. all logged users have access.
        endpoint_if_not_allowed: 
            Endpoint to redirect to if user not in allowed types to access wrapped view. 
            Defaults to None. Should be set if `allowed_types` argument given.

    Raise:
        ValueError:
            If `allowed_types` given, but `endpoint_if_not_allowed` is not.
    """
    if allowed_types and not endpoint_if_not_allowed is None or not allowed_types and endpoint_if_not_allowed:
        raise ValueError(format_message("List of allowed types to view is provided, but endpoint of not-logged users is not."))

    def decorator(view: Callable):
        @wraps(view)
        def inner(**kwargs):
            result = None
            error_message = None

            if session.get("user", None) is None:
                error_message = format_message("Reject request of unauthorized user to view: {}", view.__name__)
                result = redirect(url_for(endpoint_if_not_logged))
            # Variable `endpoint_if_not_allowed` checked here for the second time since Pyright gives error on redirect line.
            elif allowed_types is not None and endpoint_if_not_allowed:
                if session["user"]["type"] not in allowed_types:
                    error_message = format_message("Reject request of user {} with type {} to view {}.", [session["user"]["username"], session["user"]["name"], view.__name__])
                    result = redirect(url_for(endpoint_if_not_allowed))
            
            # Check if error occured, else normally call view. Finally return result with error or view output.
            if error_message is not None:
                log.warning(error_message)
            else:
                result = view(**kwargs)
            return result
        return inner
    return decorator