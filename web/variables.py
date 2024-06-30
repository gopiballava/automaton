import cherrypy
import time
from typing import Optional


class Variables:
    def __init__(self):
        pass

    @cherrypy.expose
    def index(self):
        return "Hello world"

    @cherrypy.expose
    def date(self, id: Optional[str] = None):
        return time.strftime(f"%t %d %c {id}")
