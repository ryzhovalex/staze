import re

from flask.views import MethodView
from warepy import Singleton, format_message
from staze.core.log import log

from staze.core.noconflict import makecls


class View(MethodView):
    """Presents API source with HTTP analog methods to be registered in app routing.
    
    Contains general methods `get`, `post`, `put` and `delete` according to same HTTP methods 
    and should be re-implemented in children classes.
    
    Refs:
        https://flask.palletsprojects.com/en/2.0.x/views/#method-views-for-apis
    """
    __metaclass__ = makecls()

    # Route will be the same for all methods
    ROUTE: str
    # View methods. Note that this list completely overrides HttpMethodEnum
    # for this view
    METHODS: list[str] = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
    ENDPOINT: str | None = None

    # List of decorators to apply to all view's methods.
    # decorators = [log.catch]  
    # To extend decorators in child class, use `decorators = View.decorators + [your_shiny_decorator]` 
    # in your class variable definition.

    @classmethod
    def get_transformed_route(cls) -> str:
        """Return route transformed to endpoint format.

        This method used by app to get endpoint if it's not given at assembling
        stage.
        
        Example:
        ```python
        v = ViewModel(view_class=MyViewClass, route='/my/perfect/route')
        v.get_transformed_route()
        # 'my.perfect.route'
        ```
        """
        res_route: str = ''
        route_pieces: list[str] = cls.ROUTE.split('/')

        for piece in route_pieces:
            if re.match(r'\<.+\>', piece):
                # Remove arrows around route, so /user/<id> transforms to
                # user.id
                res_route += piece[1:len(piece)-2]
            else:
                res_route += piece

        return res_route

