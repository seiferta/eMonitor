from blinker import Namespace

SIGNALDEBUG = False


class MySignal:
    app = None

    def __init__(self):
        self.signals = {}
        self.signal = Namespace()

    def init_app(self, app):
        MySignal.app = app

    def addSignal(self, classname, option):
        if MySignal.app and SIGNALDEBUG:
            MySignal.app.logger.info('signal: add %s.%s' % (classname, option))
        if '%s.%s' % (classname, option) not in self.signals.keys():
            self.signals['%s.%s' % (classname, option)] = self.signal.signal('%s.%s' % (classname, option))

    def send(self, classname, option, **extra):
        if MySignal.app and SIGNALDEBUG:
            MySignal.app.logger.info('signal: send %s.%s with: %s' % (classname, option, extra))
        if '%s.%s' % (classname, option) in self.signals.keys():
            self.signals['%s.%s' % (classname, option)].send('%s.%s' % (classname, option), **extra)

    def connect(self, classname, option, func):
        if MySignal.app and SIGNALDEBUG:
            MySignal.app.logger.info('signal: connect %s.%s func: %s' % (classname, option, func))
        if not '%s.%s' % (classname, option) in self.signals.keys():
            self.signals['%s.%s' % (classname, option)] = self.signal.signal('%s.%s' % (classname, option))
        self.signals['%s.%s' % (classname, option)].connect(func)

    def disconnect(self, classname, option, func):
        if '%s.%s' % (classname, option) in self.signals.keys():
            self.signals['%s.%s' % (classname, option)].disconnect(func)