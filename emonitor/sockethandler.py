import time
from tornado.websocket import WebSocketHandler


class SocketHandler(WebSocketHandler):
    clients = set()

    @staticmethod
    #def send_message(sender='', message='', category='', **extra):
    def send_message(sender, **extra):
        for client in SocketHandler.clients:
            #if category.split('.')[0] in client._config:
            #client.write_message(time.ctime() + '<i class="fa fa-bell-o"></i>')
            client.write_message(sender, extra)

    def open(self):
        #print "api-open"
        #if not hasattr(self, '_config'):
        #    self._config = []
        SocketHandler.clients.add(self)

    def on_close(self):
        #print "api-close"
        SocketHandler.clients.remove(self)

    #def on_message(self, message):
        #print ">>>", self in ApiHandler.clients, message

       # key, value = message.split('=')
        #if key == 'filter':
       #     self._config.append(value)