from flask import send_from_directory
from staze import View, App, log


class FaviconView(View):
    ROUTE: str = "/favicon.ico"

    def get(self):
        log.debug(App.instance().STATIC_DIR)
        return send_from_directory(App.instance().STATIC_DIR, "favicon.ico")
