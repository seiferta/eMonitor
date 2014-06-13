import yaml
import random
import subprocess
from flask import current_app
from emonitor.extensions import db, classes
from emonitor.utils import Module


class Printers(db.Model):
    __tablename__ = 'printers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    printer = db.Column(db.String(64))
    module = db.Column(db.String(64))
    layout = db.Column(db.String(64))
    _settings = db.Column('settings', db.Text)
    state = db.Column(db.INTEGER)

    def __init__(self, name, printer, module, layout, settings="", state=0):
        self.name = name
        self.printer = printer
        self.module = module
        self.layout = layout
        self._settings = settings
        self.state = state

    @property
    def settings(self):
        return yaml.load(self._settings)

    @settings.setter
    def settings(self, val):
        self._settings = yaml.safe_dump(val, encoding='utf-8')

    def getCallString(self, filename=""):  # get formated callstring
        import emonitor.webapp as wa
        callstring = classes.get('settings').get('printer.callstring')
        callstring = callstring.replace('[basepath]', wa.config.get('PROJECT_ROOT'))
        if self.printer == '<default>':  # use default printer
            callstring = callstring.replace('-printer [printer]', '')
        else:
            callstring = callstring.replace('[printer]', '"%s"' % self.printer)
        callstring = callstring.replace('[copies]', self.settings[0])
        callstring = callstring.replace('[filename]', filename)
        return callstring

    @staticmethod
    def handleEvent(eventname, *kwargs):
        import emonitor.webapp as wa

        _printer = None
        hdl = [hdl for hdl in classes.get('eventhandler').getEventhandlers(event=eventname) if hdl.handler == 'emonitor.modules.printers.printers.Printers'][0]
        if hdl:
            for p in hdl.getParameterValues('in'):
                if p[0] == 'in.printerid':
                    _printer = Printers.getPrinters(p[1])
                    break
        if _printer:
            tmpfilename = random.random()
            callstring = _printer.getCallString(filename='%s%s.pdf' % (wa.config.get('PATH_TMP'), tmpfilename))
            alarm = classes.get('alarm').getAlarms(kwargs[0]['alarmid'])
            with wa.test_request_context('/', method='get'):
                with open('%s%s.pdf' % (wa.config.get('PATH_TMP'), tmpfilename), 'wb') as tmpfile:
                    tmpfile.write(Module.getPdf(alarm.getExportData('.html', id=alarm.id, style=_printer.layout[6:-5])))
            print "printers handle", callstring
            try:
                ret = subprocess.check_output(callstring, stderr=subprocess.STDOUT, shell=False)
                print ret
            except:
                pass

    @staticmethod
    def getPrinters(pid=0):
        if pid == 0:
            return db.session.query(Printers).all()
        else:
            return db.session.query(Printers).filter_by(id=int(pid)).first()