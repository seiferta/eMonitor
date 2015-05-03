from blinker import Namespace
import logging
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MySignal:

    def __init__(self):
        self.signals = {}
        self.signal = Namespace()

    def init_app(self, app):
        pass

    def addSignal(self, classname, option):
        logger.debug('add signal {}.{}'.format(classname, option))
        if '{}.{}'.format(classname, option) not in self.signals.keys():
            self.signals['{}.{}'.format(classname, option)] = self.signal.signal('{}.{}'.format(classname, option))

    def send(self, classname, option, **extra):
        logger.debug('send signal {}.{} with: {}'.format(classname, option, extra))
        logger.info('send signal {}.{}'.format(classname, option))
        if '{}.{}'.format(classname, option) in self.signals.keys():
            payload = '{}.{}'.format(classname, option)
            if extra:
                extra['sender'] = payload
                payload = json.dumps(extra)
            self.signals['{}.{}'.format(classname, option)].send(str(payload))

    def connect(self, classname, option, func):
        logger.debug('connect signal {}.{} with func: {}()'.format(classname, option, func.__name__))
        if not '{}.{}'.format(classname, option) in self.signals.keys():
            self.signals['{}.{}'.format(classname, option)] = self.signal.signal('{}.{}'.format(classname, option))
        self.signals['{}.{}'.format(classname, option)].connect(func)

    def disconnect(self, classname, option, func):
        if '{}.{}'.format(classname, option) in self.signals.keys():
            self.signals['{}.{}'.format(classname, option)].disconnect(func)
