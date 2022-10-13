from flask import render_template, send_from_directory
from staze import View


class HomeView(View):
    ROUTE: str = "/"

    def get(self):
        return render_template("index.html")
