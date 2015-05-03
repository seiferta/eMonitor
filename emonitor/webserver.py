import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from emonitor.socketserver import SocketHandler
import logging

SUBSCRIBERS = set()


class Root(object):
    @cherrypy.expose
    #@cherrypy.tools.websocket(on=False)
    def ws(self):
        return """test"""

    @cherrypy.expose
    def index(self):
        cherrypy.log("Handler created: {}".format(cherrypy.request.ws_handler))


def webserver(app):
    # init logger for webserver modules
    loggerws4py = logging.getLogger('ws4py')
    loggerws4py.setLevel(app.config.get('LOGLEVEL', logging.ERROR))
    loggercherry = logging.getLogger('cherrypy')
    loggercherry.setLevel(app.config.get('LOGLEVEL', logging.ERROR))
    loggercherry = logging.getLogger('cherrypy.error')
    loggercherry.setLevel(app.config.get('LOGLEVEL', logging.ERROR))

    cherrypy.server.unsubscribe()
    cherrypy.tree.graft(app, '/')
    if app.config.get('service', False):  # log to file if used as service
        cherrypy.config.update({'log.error_file': '{}/service.log'.format(app.config.get('PATH_DATA')), 'log.screen': False})
    cherrypy.config.update({'engine.autoreload.on': False, 'engine.SIGHUP': None, 'engine.SIGTERM': None, 'environment': 'embedded'})
    cherrypy.server.thread_pool = app.config.get('SERVER_THREADS', 30)
    cherrypy.server.thread_pool_max = 50
    cherrypy.server.socket_port = int(app.config.get('PORT'))
    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.log.screen = False

    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()
    cherrypy.tree.mount(Root(), '/ws', config={'/': {'tools.websocket.on': True, 'tools.trailing_slash.on': False, 'tools.websocket.handler_cls': SocketHandler}})
    cherrypy.server.subscribe()

    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()
