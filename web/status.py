import cherrypy
from jinja2 import Environment, FileSystemLoader
import os


class Status:
    def __init__(self):
        self._env = Environment(
            loader=FileSystemLoader(
                [os.path.join(os.path.dirname(__file__), "templates")]
            )
        )

    @cherrypy.expose
    def index(self):
        tmpl = self._env.get_template("status.html")
        return tmpl.render(salutation="Hello", target="World")
