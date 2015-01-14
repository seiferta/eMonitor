import os
import time
import imp
from flask import send_from_directory, abort, Response
from emonitor.sockethandler import SocketHandler
from emonitor.utils import Module
from emonitor.extensions import classes, db, events, scheduler, babel, signal
from emonitor.modules.settings.settings import Settings
from .content_admin import getAdminContent, getAdminData
from .content_frontend import getFrontendContent, getFrontendData
from .alarmutils import AlarmFaxChecker, AlarmRemarkWidget, AlarmWidget, AlarmIncomeWidget, AlarmTimerWidget


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
        app.jinja_loader.searchpath.append("%s/emonitor/modules/alarms/templates" % app.config.get('PROJECT_ROOT'))

        # subnavigation
        self.adminsubnavigation = [('/admin/alarms', 'alarms.base'), ('/admin/alarms/types', 'module.alarms.types'), ('/admin/alarms/test', 'module.alarms.test')]
        
        # create database tables
        from .alarm import Alarm
        from .alarmhistory import AlarmHistory 
        from .alarmattribute import AlarmAttribute
        from .alarmsection import AlarmSection
        from .alarmtype import AlarmType
        classes.add('alarm', Alarm)
        classes.add('alarmattribute', AlarmAttribute)
        classes.add('alarmhistory', AlarmHistory)
        classes.add('alarmsection', AlarmSection)
        classes.add('alarmtype', AlarmType)
        db.create_all()

        self.widgets = [AlarmIncomeWidget('alarms_income'), AlarmWidget('alarms'), AlarmTimerWidget('alarms_timer'), AlarmRemarkWidget('alarms_remark')]
        
        # eventhandlers
        for f in [f for f in os.listdir('%s/emonitor/modules/alarms/inc/' % app.config.get('PROJECT_ROOT')) if f.endswith('.py')]:
            if not f.startswith('__'):
                cls = imp.load_source('emonitor.modules.alarms.inc', 'emonitor/modules/alarms/inc/%s' % f)
                checker = getattr(cls, cls.__all__[0])()
                if isinstance(checker, AlarmFaxChecker) and checker.getId() != 'Dummy':
                    events.addEvent('alarm_added.%s' % checker.getId(), handlers=[], parameters=['out.alarmid'])
                    events.addEvent('alarm_changestate.%s' % checker.getId(), handlers=[], parameters=['out.alarmid', 'out.state'])

        events.addEvent('alarm_added', handlers=[], parameters=['out.alarmid'])  # for all checkers
        events.addEvent('alarm_changestate', handlers=[], parameters=['out.alarmid', 'out.state'])  # for all checkers
        
        events.addHandlerClass('file_added', 'emonitor.modules.alarms.alarm.Alarms', Alarm.handleEvent, ['in.text', 'out.id', 'out.fields'])
        events.addHandlerClass('file_added', 'emonitor.modules.alarms.alarmtype.AlarmTypes', AlarmType.handleEvent, ['in.text', 'out.type'])

        # signals and handlers
        signal.addSignal('alarm', 'changestate')
        signal.addSignal('alarm', 'added')
        signal.addSignal('alarm', 'updated')
        signal.connect('alarm', 'changestate', frontendAlarmHandler.handleAlarmChanges)
        signal.connect('alarm', 'added', frontendAlarmHandler.handleAlarmChanges)
        signal.connect('alarm', 'updated', frontendAlarmHandler.handleAlarmChanges)
        signal.connect('alarm', 'deleted', frontendAlarmHandler.handleAlarmChanges)

        signal.connect('alarm', 'testupload_start', adminAlarmHandler.handleAlarmTestUpload)

        # static folders
        @app.route('/alarms/inc/<path:filename>')
        def alarms_static(filename):
            return send_from_directory("%s/emonitor/modules/alarms/inc/" % app.config.get('PROJECT_ROOT'), filename)

        @app.route('/alarms/export/<path:filename>')  # filename = [id]-[style].pdf
        def export_static(filename):
            filename, extension = os.path.splitext(filename)
            id, template = filename.split('-')
            if extension not in ['.pdf', '.html', '.png']:
                abort(404)
            elif extension == '.pdf':
                return Response(Module.getPdf(Alarm.getExportData('.html', id=id, style=template)), mimetype="application/pdf")
            elif extension == '.html':
                return Response(Alarm.getExportData(extension, id=id, style=template), mimetype="text/html")
            elif extension == '.png':
                return Response(Alarm.getExportData(extension, id=id, style=template, filename=filename), mimetype="image/png")
            
        # translations
        babel.gettext(u'module.alarms')
        babel.gettext(u'alarms.base')
        babel.gettext(u'module.alarms.types')
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

        # init
        # Do init script for alarms at start and add active alarms (state = 1)
        #from modules.alarms.alarm import Alarm
        #from core.extensions import classes, scheduler, events
        aalarms = classes.get('alarm').getActiveAlarms()  # get last active alarm
        
        if aalarms:  # add active alarm and closing time
            try:
                for aalarm in aalarms:
                    scheduler.add_job(events.raiseEvent, args=['alarm_added', dict({'alarmid': aalarm.id})])
                    closingtime = time.mktime(aalarm.timestamp.timetuple()) + float(Settings.get('alarms.autoclose', 1800))

                    if closingtime > time.time():  # add close event
                        scheduler.add_job(Alarm.changeState, args=[aalarm.id, 2])
                    else:
                        scheduler.add_job(Alarm.changeState, args=[aalarm.id, 2])
            except:
                app.logger.error('alarms.__init__.py: aalarm error')

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
        SocketHandler.send_message(extra)
