from ws4py.websocket import WebSocket
import json

SUBSCRIBERS = set()  # set holds all active connections


class SocketHandler(WebSocket):
    """
    handler for socketserver to deliver messages
    """
    def __init__(self, *args, **kw):
        WebSocket.__init__(self, *args, **kw)
        SUBSCRIBERS.add(self)

    def closed(self, code, reason=None):
        SUBSCRIBERS.remove(self)

    @staticmethod
    def send_message(payload, **extra):
        if extra:
            extra['sender'] = payload
            payload = json.dumps(extra)
        for subscriber in SUBSCRIBERS:
            subscriber.send(payload)

    def received_message(self, message):
        for subscr in SUBSCRIBERS:
            subscr.send(message.data, message.is_binary)
