from .extensions import signal
from tornado.websocket import WebSocketHandler


class SocketHandler(WebSocketHandler):
    clients = set()

    @staticmethod
    def send_message(sender, **extra):
        for client in SocketHandler.clients:
            if extra:
                extra['sender'] = sender
                client.write_message(extra)
            else:
                client.write_message(sender, extra)

    def data_received(self, chunk):
        pass

    def open(self):
        SocketHandler.clients.add(self)

    def on_close(self):
        SocketHandler.clients.remove(self)

    def on_message(self, message):
        _op, _cls, _msg = message.split('.')

        if _op == 'add':
            signal.addSignal(_cls, _msg)
        elif _op == 'send':
            signal.signals[_cls + '.' + _msg].send('')
