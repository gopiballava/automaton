import cherrypy
from .status import Status
from .variables import Variables


class Core:
    def __init__(self, local_test: bool = False):
        self._local_test = local_test

    def run(self):
        cherrypy.tree.mount(Status(), "/status", {})
        cherrypy.tree.mount(Variables(), "/variables", {})
        # TODO: Add the sensor stuff!

        cherrypy.config.update({'server.socket_port': 9090})
        cherrypy.config.update({'server.socket_host': '0.0.0.0'})
        cherrypy.engine.start()
        cherrypy.engine.block()
