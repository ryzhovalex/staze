from flask.views import MethodView
from warepy import Singleton, format_message
from staze.tools.log import log

from staze.tools.noconflict import makecls


class View(MethodView):
    """Presents API source with HTTP analog methods to be registered in app routing.
    
    Contains general methods `get`, `post`, `put` and `delete` according to same HTTP methods 
    and should be re-implemented in children classes.
    
    Refs:
        https://flask.palletsprojects.com/en/2.0.x/views/#method-views-for-apis
    """
    __metaclass__ = makecls()

    # List of decorators to apply to all view's methods.
    # decorators = [log.catch]  
    # To extend decorators in child class, use `decorators = View.decorators + [your_shiny_decorator]` 
    # in your class variable definition.

    def get(self):
        error_message = format_message("Method GET is not implemented at view: {}", self.__class__.__name__)
        raise NotImplementedError(error_message)
    
    def post(self):
        error_message = format_message("Method POST is not implemented at view: {}", self.__class__.__name__)
        raise NotImplementedError(error_message)

    def put(self):
        error_message = format_message("Method PUT is not implemented at view: {}", self.__class__.__name__)
        raise NotImplementedError(error_message)

    def delete(self):
        error_message = format_message("Method DELETE is not implemented at view: {}", self.__class__.__name__)
        raise NotImplementedError(error_message)
