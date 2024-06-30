import cherrypy
from .status import Status
from .variables import Variables


class Core:
    def __init__(self, local_test: bool = False):
        self._local_test = local_test

    def run(self):
        cherrypy.tree.mount(Status(), "/status", {})
        cherrypy.tree.mount(Variables(), "/variables", {})
        cherrypy.engine.start()
        cherrypy.engine.block()
