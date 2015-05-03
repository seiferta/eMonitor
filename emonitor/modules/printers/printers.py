import os
import yaml
import random
import subprocess
import time
import logging
from sqlalchemy import and_
from emonitor.extensions import db
from emonitor.utils import Module
from printerutils import PrintLayout
from emonitor.modules.settings.settings import Settings
from emonitor.modules.events.eventhandler import Eventhandler

logger = logging.getLogger(__name__)


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

    def getCallString(self, pdffilename="", **params):  # get formated callstring
        from emonitor import app
        callstring = Settings.get('printer.callstring')
        callstring = callstring.replace('[basepath]', app.config.get('PROJECT_ROOT'))
        if self.printer == '<default>':  # use default printer
            callstring = callstring.replace('-printer [printer]', '')
        else:
            if 'printer' in params:
                callstring = callstring.replace('[printer]', '"{}"'.format(params['printer']))
            else:
                callstring = callstring.replace('[printer]', '"{}"'.format(self.printer))
        try:
            if 'copies' in params:
                callstring = callstring.replace('[copies]', "{}".format(params['copies']))
            else:
                callstring = callstring.replace('[copies]', self.settings[0])
        except IndexError:
            callstring = callstring.replace('[copies]', '1')
        callstring = callstring.replace('[filename]', pdffilename)
        return callstring

    def doPrint(self, **params):
        """
        Start printout of defined object

        :param params: checks for *alarmid*
        """
        from emonitor import app
        pl = PrintLayout('{}.{}'.format(self.module, self.layout))
        _params = {}
        for p in pl.getParameters(self.settings[1].split(';')):  # load parameters from printer definition
            _params[p.getFullName()] = p.getFormatedValue()
        tmpfilename = random.random()
        callstring = self.getCallString(pdffilename='{}{}.pdf'.format(app.config.get('PATH_TMP'), tmpfilename), **params)
        if "id" in params:
            with app.test_request_context('/', method='get'):
                with open('{}{}.pdf'.format(app.config.get('PATH_TMP'), tmpfilename), 'wb') as tmpfile:
                    _params['id'] = params['id']
                    _params['style'] = self.layout[6:-5]
                    tmpfile.write(Module.getPdf(params['object'].getExportData('.html', **_params)))
            try:
                subprocess.check_output(callstring, stderr=subprocess.STDOUT, shell=True)
                os.remove('{}{}.pdf'.format(app.config.get('PATH_TMP'), tmpfilename))
            except WindowsError:
                pass

    @staticmethod
    def handleEvent(eventname, **kwargs):
        """
        Event handler for printer class, adds own processing time

        :param eventname: *emonitor.modules.printers.printers.Printers*
        :param kwargs: *mode*=*test*, *time*,
        :return: kwargs
        """
        stime = time.time()
        _printer = None
        hdl = [hdl for hdl in Eventhandler.getEventhandlers(event=eventname) if hdl.handler == 'emonitor.modules.printers.printers.Printers'][0]
        if hdl:
            for p in hdl.getParameterValues('in'):
                if p[0] == 'in.printerid':
                    _printer = Printers.getPrinters(p[1])
                    break

        state = ""
        if _printer:
            try:
                if kwargs['mode'] != 'test':
                    if '{}id'.format(_printer.module[:-1]) in kwargs.keys():  # add object and id if given
                        kwargs['id'] = kwargs['{}id'.format(_printer.module[:-1])]
                        for key, cls in db.Model._decl_class_registry.iteritems():
                            if key.lower() == _printer.module[:-1]:
                                kwargs['object'] = cls
                                break
                    _printer.doPrint(**dict(kwargs))
                else:
                    state = "(testmode)"
            except KeyError:
                state = "with errors"
        else:
            state = "with error 'no printer found'"

        if 'time' not in kwargs.keys():
            kwargs['time'] = []
        kwargs['time'].append(u"printer: print done {} in {} sec.".format(state, time.time() - stime))

        return kwargs

    @staticmethod
    def getPrinters(pid=0):
        """
        Get list of printers definitions filtered by parameters

        :param pid: id of printerdefinition or *0* for all definitions
        :return: list of :py:class:`emonitor.modules.printers.printers.Printers`
        """
        if pid == 0:
            return Printers.query.all()
        else:
            return Printers.query.filter_by(id=int(pid)).first()

    @staticmethod
    def getActivePrintersOfModule(module):
        """
        Get list of active definitions for given modulename

        :param module: modulename
        :return: list of :py:class:`emonitor.modules.printers.printers.Printers`
        """
        return Printers.query.filter(and_(Printers.module == module, Printers.state == '1')).all()
