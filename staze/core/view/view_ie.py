from dataclasses import dataclass
import re

from staze.core.ie.ie import Ie

from .view import View


@dataclass
class ViewIe(Ie):
    route: str  # Route will be the same for all methods.
    view_class: type[View]
    endpoint: str | None = None

    def get_transformed_route(self) -> str:
        """Return route transformed to endpoint format.

        This method used by app to get endpoint if it's not given at assembling
        stage.
        
        Example:
        ```python
        v = ViewIe(view_class=MyViewClass, route='/my/perfect/route')
        v.get_transformed_route()
        # 'my.perfect.route'
        ```
        """
        res_route: str = ''
        route_pieces: list[str] = self.route.split('/')

        for piece in route_pieces:
            if re.match(r'\<.+\>', piece):
                # Remove arrows around route, so /user/<id> transforms to
                # user.id
                res_route += piece[1:len(piece)-2]
            else:
                res_route += piece

        return res_route
