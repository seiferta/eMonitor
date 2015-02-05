import os
import yaml
import random
import subprocess
import time
from sqlalchemy import and_
from emonitor.extensions import db, classes
from emonitor.utils import Module
from printerutils import PrintLayout


class Printers(db.Model):
    """Printers class"""
    __tablename__ = 'printers'
    __table_args__ = {'extend_existing': True}

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

    def getCallString(self, filename="", **params):  # get formated callstring
        import emonitor.webapp as wa
        callstring = classes.get('settings').get('printer.callstring')
        callstring = callstring.replace('[basepath]', wa.config.get('PROJECT_ROOT'))
        if self.printer == '<default>':  # use default printer
            callstring = callstring.replace('-printer [printer]', '')
        else:
            if 'printer' in params:
                callstring = callstring.replace('[printer]', '"%s"' % params['printer'])
            else:
                callstring = callstring.replace('[printer]', '"%s"' % self.printer)
        try:
            if 'copies' in params:
                callstring = callstring.replace('[copies]', "{}".format(params['copies']))
            else:
                callstring = callstring.replace('[copies]', self.settings[0])
        except IndexError:
            callstring = callstring.replace('[copies]', '1')
        callstring = callstring.replace('[filename]', filename)
        return callstring

    def doPrint(self, **params):
        """
        Start printout of defined object

        :param params: checks for *alarmid*
        """
        import emonitor.webapp as wa
        pl = PrintLayout('%s.%s' % (self.module, self.layout))
        _params = {}
        for p in pl.getParameters(self.settings[1].split(';')):  # load parameters from printer definition
            _params[p.getFullName()] = p.getFormatedValue()
        tmpfilename = random.random()
        callstring = self.getCallString(filename='%s%s.pdf' % (wa.config.get('PATH_TMP'), tmpfilename), **params)
        if "id" in params:
            with wa.test_request_context('/', method='get'):
                with open('%s%s.pdf' % (wa.config.get('PATH_TMP'), tmpfilename), 'wb') as tmpfile:
                    _params['id'] = params['id']
                    _params['style'] = self.layout[6:-5]
                    tmpfile.write(Module.getPdf(params['object'].getExportData('.html', **_params)))
            try:
                subprocess.check_output(callstring, stderr=subprocess.STDOUT, shell=True)
                os.remove('%s%s.pdf' % (wa.config.get('PATH_TMP'), tmpfilename))
            except WindowsError:
                pass

    @staticmethod
    def handleEvent(eventname, *kwargs):
        """
        Event handler for printer class, adds own processing time

        :param eventname: *emonitor.modules.printers.printers.Printers*
        :param kwargs: *mode*=*test*, *time*,
        :return: kwargs
        """
        stime = time.time()
        _printer = None
        hdl = [hdl for hdl in classes.get('eventhandler').getEventhandlers(event=eventname) if hdl.handler == 'emonitor.modules.printers.printers.Printers'][0]
        if hdl:
            for p in hdl.getParameterValues('in'):
                if p[0] == 'in.printerid':
                    _printer = Printers.getPrinters(p[1])
                    break

        state = ""
        if _printer:
            try:
                if kwargs[0]['mode'] != 'test':
                    if '%sid' % _printer.module[:-1] in kwargs[0]:  # add obkect and id if given
                        kwargs[0]['id'] = kwargs[0]['%sid' % _printer.module[:-1]]
                        kwargs[0]['object'] = classes.get(_printer.module[:-1])
                    _printer.doPrint(**dict(kwargs[0]))
                else:
                    state = "(testmode) "
            except KeyError:
                state = "with errors "
        else:
            state = "with error 'no printer found' "

        if 'time' not in kwargs[0]:
            kwargs[0]['time'] = []
        kwargs[0]['time'].append('printer: print done %sin %s sec.' % (state, time.time() - stime))

        return kwargs

    @staticmethod
    def getPrinters(pid=0):
        """
        Get list of printers definitions filtered by parameters

        :param pid: id of printerdefinition or *0* for all definitions
        :return: list of :py:class:`emonitor.modules.printers.printers.Printers`
        """
        if pid == 0:
            return db.session.query(Printers).all()
        else:
            return db.session.query(Printers).filter_by(id=int(pid)).first()

    @staticmethod
    def getActivePrintersOfModule(module):
        """
        Get list of active definitions for given modulename

        :param module: modulename
        :return: list of :py:class:`emonitor.modules.printers.printers.Printers`
        """
        return db.session.query(Printers).filter(and_(Printers.module == module, Printers.state == '1')).all()
