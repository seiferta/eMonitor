import os
import imp
import logging
from flask import send_from_directory, abort, Response, request
from emonitor.socketserver import SocketHandler
from emonitor.utils import Module
from emonitor.extensions import events, babel, signal
from emonitor.modules.alarms.content_admin import getAdminContent, getAdminData
from emonitor.modules.alarms.content_frontend import getFrontendContent, getFrontendData
from emonitor.modules.alarms.alarmutils import AlarmFaxChecker, AlarmRemarkWidget, AlarmWidget, AlarmIncomeWidget, AlarmTimerWidget

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


class AlarmsModule(Module):
    """
    Definition of alarms module with frontend, admin and widget area
    """
    info = dict(area=['admin', 'frontend', 'widget'], messages=['add', 'info', 'activate', 'close'], name='alarms', path='alarms', icon='fa-fire', version='0.2')
    
    def __repr__(self):
        return "alarms"

    def __init__(self, app):
        """
        Add specific parameters and configuration to app object

        :param app: flask wsgi application
        """
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("{}/emonitor/modules/alarms/templates".format(app.config.get('PROJECT_ROOT')))

        # subnavigation
        self.adminsubnavigation = [('/admin/alarms', 'alarms.base'), ('/admin/alarms/types', 'module.alarms.types'), ('/admin/alarms/report', 'module.alarms.report'), ('/admin/alarms/config', 'module.alarms.config'), ('/admin/alarms/test', 'module.alarms.test')]
        
        # create database tables
        from emonitor.modules.alarms.alarm import Alarm
        from emonitor.modules.alarms.alarmhistory import AlarmHistory
        from emonitor.modules.alarms.alarmattribute import AlarmAttribute
        from emonitor.modules.alarms.alarmsection import AlarmSection
        from emonitor.modules.alarms.alarmtype import AlarmType

        self.widgets = [AlarmIncomeWidget('alarms_income'), AlarmWidget('alarms'), AlarmTimerWidget('alarms_timer'), AlarmRemarkWidget('alarms_remark')]
        
        # eventhandlers
        for f in [f for f in os.listdir('{}/emonitor/modules/alarms/inc/'.format(app.config.get('PROJECT_ROOT'))) if f.endswith('.py')]:
            if not f.startswith('__'):
                cls = imp.load_source('emonitor.modules.alarms.inc', '{}/emonitor/modules/alarms/inc/{}'.format(app.config.get('PROJECT_ROOT'), f))
                checker = getattr(cls, cls.__all__[0])()
                if isinstance(checker, AlarmFaxChecker) and checker.getId() != 'Dummy':
                    for at in AlarmType.getAlarmTypes():
                        if at.interpreter == f:
                            events.addEvent('alarm_added.{}'.format(at.name), handlers=[], parameters=['out.alarmid'])
                            events.addEvent('alarm_changestate.{}'.format(at.name), handlers=[], parameters=['out.alarmid', 'out.state'])

        events.addEvent('alarm_added', handlers=[], parameters=['out.alarmid'])  # for all checkers
        events.addEvent('alarm_changestate', handlers=[], parameters=['out.alarmid', 'out.state'])  # for all checkers
        
        events.addHandlerClass('file_added', 'emonitor.modules.alarms.alarm.Alarms', Alarm.handleEvent, ['in.text', 'out.id', 'out.fields'])
        events.addHandlerClass('file_added', 'emonitor.modules.alarms.alarmtype.AlarmTypes', AlarmType.handleEvent, ['in.text', 'out.type'])

        events.addHandlerClass('incoming_serial_data', 'emonitor.modules.alarms.alarm.Alarms', Alarm.handleSerialEvent, ['in.text', 'out.id', 'out.fields'])
        events.addHandlerClass('incoming_serial_data', 'emonitor.modules.alarms.alarmtype.AlarmTypes', AlarmType.handleEvent, ['in.text', 'out.type'])

        # signals and handlers
        signal.addSignal('alarm', 'changestate')
        signal.addSignal('alarm', 'added')
        signal.addSignal('alarm', 'updated')
        signal.addSignal('alarm', 'error')
        signal.connect('alarm', 'changestate', frontendAlarmHandler.handleAlarmChanges)
        signal.connect('alarm', 'added', frontendAlarmHandler.handleAlarmChanges)
        signal.connect('alarm', 'updated', frontendAlarmHandler.handleAlarmChanges)
        signal.connect('alarm', 'deleted', frontendAlarmHandler.handleAlarmChanges)
        signal.connect('alarm', 'error', frontendAlarmHandler.handleAlarmErrors)

        signal.connect('alarm', 'testupload_start', adminAlarmHandler.handleAlarmTestUpload)

        # static folders
        @app.route('/alarms/inc/<path:filename>')
        def alarms_static(filename):
            if filename.startswith('sample_'):  # deliver sample checker file
                clsname = filename.split('_')[1]
                return Response(AlarmType.getAlarmTypes(clsname).interpreterclass().getSampleLayout(), mimetype="image/jpeg")

            return send_from_directory("{}/emonitor/modules/alarms/inc/".format(app.config.get('PROJECT_ROOT')), filename)

        @app.route('/alarms/export/<path:filename>')  # filename = [id]-[style].pdf
        def export_static(filename):
            filename, extension = os.path.splitext(filename)
            try:
                id, template = filename.split('-')
                if extension not in ['.pdf', '.html', '.png']:
                    abort(404)
                elif extension == '.pdf':
                    return Response(Module.getPdf(Alarm.getExportData('.html', id=id, style=template, args=request.args)), mimetype="application/pdf")
                elif extension == '.html':
                    return Response(Alarm.getExportData(extension, id=id, style=template, args=request.args), mimetype="text/html")
                elif extension == '.png':
                    return Response(Alarm.getExportData(extension, id=id, style=template, filename=filename, args=request.args), mimetype="image/png")
            except ValueError:
                return abort(404)

        # add reportfolder
        if not os.path.exists('{}/alarmreports/'.format(app.config.get('PATH_DATA'))):
            os.makedirs('{}/alarmreports/'.format(app.config.get('PATH_DATA')))
            
        # translations
        babel.gettext(u'module.alarms')
        babel.gettext(u'alarms.base')
        babel.gettext(u'module.alarms.types')
        babel.gettext(u'module.alarms.report')
        babel.gettext(u'module.alarms.config')
        babel.gettext(u'module.alarms.test')
        babel.gettext(u'alarms_income')
        babel.gettext(u'alarms_timer')
        babel.gettext(u'alarms_remark')
        babel.gettext(u'alarms')
        babel.gettext(u'alarms.prio0')
        babel.gettext(u'alarms.prio1')
        babel.gettext(u'alarms.prio2')
        babel.gettext(u'emonitor.modules.alarms.alarm.Alarms')
        babel.gettext(u'emonitor.modules.alarms.alarmtype.AlarmTypes')
        babel.gettext(u'alarms.test.protocol')
        babel.gettext(u'alarms.test.result')
        babel.gettext(u'alarmstate.active')
        babel.gettext(u'alarmstate.created')
        babel.gettext(u'alarmstate.done')
        babel.gettext(u'alarmstate.archive')
        babel.gettext(u'active')
        babel.gettext(u'created')
        babel.gettext(u'done')
        babel.gettext(u'archive')
        babel.gettext(u'alarms.statechangeactivated')
        babel.gettext(u'alarms.prioshort0')
        babel.gettext(u'alarms.prioshort1')
        babel.gettext(u'alarms.prioshort2')
        babel.gettext(u'alarms.carsinuse')
        babel.gettext(u'history.autochangeState')
        babel.gettext(u'history.message')
        babel.gettext(u'trigger.alarm_added')
        babel.gettext(u'trigger.alarm_changestate')

        babel.gettext(u'trigger.alarm_added_sub')
        babel.gettext(u'trigger.alarm_changestate_sub')

        babel.gettext(u'alarms.print.slightleft')
        babel.gettext(u'alarms.print.slightright')
        babel.gettext(u'alarms.print.right')
        babel.gettext(u'alarms.print.left')
        babel.gettext(u'alarms.print.straight')
        babel.gettext(u'alarms.print.exit')
        babel.gettext(u'alarms.print.bus')
        babel.gettext(u'alarms.print.positive')
        babel.gettext(u'alarms.print.negative')

        babel.gettext(u'alarms.filter.0')
        babel.gettext(u'alarms.filter.1')
        babel.gettext(u'alarms.filter.7')
        babel.gettext(u'alarms.filter.31')

        babel.gettext(u'internal')
        babel.gettext(u'external')

        babel.gettext(u'AFAlerting')
        babel.gettext(u'AFCars')
        babel.gettext(u'AFMaterial')
        babel.gettext(u'AFReport')
        babel.gettext(u'AFTime')
        babel.gettext(u'AFDamage')
        babel.gettext(u'AFOthers')
        babel.gettext(u'AFPersons')

        babel.gettext(u'alarms.fields.simple')
        babel.gettext(u'alarms.fields.extended')
        babel.gettext(u'alarms.fields.persons.field.sum')
        babel.gettext(u'alarms.fields.persons.field.house')
        babel.gettext(u'alarms.fields.persons.field.pa_alarm')
        babel.gettext(u'alarms.fields.persons.field.el')
        babel.gettext(u'alarms.fields.persons.field.alarm')
        babel.gettext(u'alarms.fields.persons.field.pa')
        babel.gettext(u'alarms.fields.persons.field.pa_house')
        babel.gettext(u'alarms.fields.persons.field.elgrade')
        babel.gettext(u'alarms.fields.persons.field.style.simple')
        babel.gettext(u'alarms.fields.persons.field.style.extended')

        # init
        # Do init script for alarms at start and add alarms (state = 1 or 2) (active or done)
        for aalarm in Alarm.query.filter(Alarm.state == 1 or Alarm.state == 2).all():
            aalarm.updateSchedules(reference=1)

    def frontendContent(self):
        return 1

    def getAdminContent(self, **params):
        """
        Call *getAdminContent* of alarms class

        :param params: send given parameters to :py:class:`emonitor.modules.alarms.content_admin.getAdminContent`
        """
        return getAdminContent(self, **params)

    def getAdminData(self):
        """
        Call *getAdminData* method of alarms class and return values

        :return: return result of method
        """
        return getAdminData(self)

    def getFrontendContent(self, **params):
        """
        Call *getFrontendContent* of alarms class

        :param params: send given parameters to :py:class:`emonitor.modules.alarms.content_frontend.getFrontendContent`
        """
        return getFrontendContent(**params)
        
    def getFrontendData(self):
        """
        Call *getFrontendData* of alarms class
        """
        return getFrontendData(self)


class frontendAlarmHandler(SocketHandler):
    """
    Handler class for frontend socked events of alarms
    """
    @staticmethod
    def handleAlarmChanges(sender, **extra):
        """
        Implementation of changes in alarm states

        :param sender: event sender
        :param extra: extra parameters for event
        """
        SocketHandler.send_message(sender, **extra)

    @staticmethod
    def handleAlarmErrors(sender, **extra):
        """
        Implementation of error in alarms

        :param sender: event sender
        :param extra: extra parameters for event
        """
        SocketHandler.send_message(sender, **extra)


class adminAlarmHandler(SocketHandler):
    """
    Handler class for admin socked events of alarms
    """
    @staticmethod
    def handleAlarmTestUpload(sender, **extra):
        """
        Implementation of test upload of alarm files

        :param sender: event sender
        :param extra: extra parameters for event
        """
        SocketHandler.send_message(sender, **extra)
