from flask import send_from_directory

from emonitor.sockethandler import SocketHandler
from emonitor.extensions import db, classes, babel, signal
from emonitor.utils import Module
from emonitor.widget.monitorwidget import MonitorWidget
from .content_admin import getAdminContent, getAdminData
from .content_frontend import getFrontendContent, getFrontendData


class MonitorsModule(Module):
    info = dict(area=['admin', 'frontend', 'widget'], name='monitors', path='monitors', icon='fa-desktop', version='0.1')

    def __repr__(self):
        return "monitors"
    
    def __init__(self, app):
        Module.__init__(self, app)

        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/monitors/templates" % app.config.get('PROJECT_ROOT'))

        # subnavigation
        self.adminsubnavigation = [('/admin/monitors', 'monitors.definition'), ('/admin/monitors/style', 'module.monitors.style'), ('/admin/monitors/current', 'module.monitors.current'), ('/admin/monitors/actions', 'module.monitors.actions')]

        self.widgets = [MonitorWidget('placeholder', size=(1, 1), template='widget.placeholder.html')]
        
        # create database tables
        from .monitor import Monitor
        from .monitorlayout import MonitorLayout
        classes.add('monitor', Monitor)
        classes.add('monitorlayout', MonitorLayout)
        db.create_all()

        signal.connect('monitorserver', 'clientsearchdone', frontendMonitorHandler.handleClientSearch)

        # static folders
        @app.route('/monitors/inc/<path:filename>')
        def monitors_static(filename):
            return send_from_directory("%s/emonitor/modules/monitors/inc/" % app.config.get('PROJECT_ROOT'), filename)
            
        # translations
        babel.gettext(u'module.monitors')
        babel.gettext(u'monitors.definition')
        babel.gettext(u'module.monitors.style')
        babel.gettext(u'module.monitors.current')
        babel.gettext(u'module.monitors.actions')
        babel.gettext(u'monitors.landscape')
        babel.gettext(u'monitors.portrait')
        babel.gettext(u'monitors.orientation.0')
        babel.gettext(u'monitors.orientation.1')
        babel.gettext(u'placeholder')

    def checkDefinition(self):
        if db.session.query(classes.get('monitor')).count() == 0:
            return Module.INITNEEDED
        return Module.CHECKOK

    def getAdminContent(self, **params):
        return getAdminContent(self, **params)

    def getAdminData(self):
        return getAdminData(self)

    def getFrontendContent(self, **params):
        return getFrontendContent(self, **params)

    def getFrontendData(self):
        return getFrontendData(self)
   
    @staticmethod
    def handleEvent(eventname, *kwargs):
        kwargs[0]['monitors_ret'] = 'yyy'
        from time import sleep
        
        sleep(10)
        return kwargs


class frontendMonitorHandler(SocketHandler):
    @staticmethod
    def handleClientSearch(sender, **extra):
        SocketHandler.send_message(extra)