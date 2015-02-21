from blinker import Namespace
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MySignal:

    def __init__(self):
        self.signals = {}
        self.signal = Namespace()

    def init_app(self, app):
        pass

    def addSignal(self, classname, option):
        logger.debug('add signal %s.%s' % (classname, option))
        if '%s.%s' % (classname, option) not in self.signals.keys():
            self.signals['%s.%s' % (classname, option)] = self.signal.signal('%s.%s' % (classname, option))

    def send(self, classname, option, **extra):
        logger.info('send signal %s.%s with: %s' % (classname, option, extra))
        if '%s.%s' % (classname, option) in self.signals.keys():
            self.signals['%s.%s' % (classname, option)].send('%s.%s' % (classname, option), **extra)

    def connect(self, classname, option, func):
        logger.debug('connect signal %s.%s with func: %s()' % (classname, option, func.__name__))
        if not '%s.%s' % (classname, option) in self.signals.keys():
            self.signals['%s.%s' % (classname, option)] = self.signal.signal('%s.%s' % (classname, option))
        self.signals['%s.%s' % (classname, option)].connect(func)

    def disconnect(self, classname, option, func):
        if '%s.%s' % (classname, option) in self.signals.keys():
            self.signals['%s.%s' % (classname, option)].disconnect(func)
