from flask import send_from_directory

from emonitor.socketserver import SocketHandler
from emonitor.extensions import babel, signal
from emonitor.utils import Module
from emonitor.modules.monitors.monitor import Monitor, PlaceholderWidget
from emonitor.modules.monitors.monitorlayout import MonitorLayout
from emonitor.modules.monitors.content_admin import getAdminContent, getAdminData
from emonitor.modules.monitors.content_frontend import getFrontendData


class MonitorsModule(Module):
    """
    Definition of monitor module with frontend, admin and widget area
    """
    info = dict(area=['admin', 'frontend', 'widget'], name='monitors', path='monitors', icon='fa-desktop', version='0.1')

    def __repr__(self):
        return "monitors"
    
    def __init__(self, app):
        Module.__init__(self, app)

        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/monitors/templates" % app.config.get('PROJECT_ROOT'))

        # subnavigation
        self.adminsubnavigation = [('/admin/monitors', 'monitors.definition'), ('/admin/monitors/style', 'module.monitors.style'), ('/admin/monitors/current', 'module.monitors.current'), ('/admin/monitors/actions', 'module.monitors.actions')]
        self.widgets = [PlaceholderWidget('placeholder')]

        signal.connect('monitorserver', 'clientsearchdone', frontendMonitorHandler.handleClientSearch)
        signal.connect('monitorserver', 'clientanswer', frontendMonitorHandler.handleClientAnswer)

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
        if Monitor.query.count() == 0:
            return Module.INITNEEDED
        return Module.CHECKOK

    def getAdminContent(self, **params):
        """
        Call *getAdminContent* of monitor class

        :param params: send given parameters to :py:class:`emonitor.modules.monitors.content_admin.getAdminContent`
        """
        return getAdminContent(self, **params)

    def getAdminData(self):
        """
        Call *getAdminData* method of monitors class and return values

        :return: return result of method
        """
        return getAdminData(self)

    def getFrontendData(self):
        """
        Call *getFrontendData* of monitors class
        """
        from emonitor.modules.monitors.content_frontend import getFrontendData
        return getFrontendData(self)
   
    @staticmethod
    def handleEvent(eventname, **kwargs):
        """DEPRECATED test method"""
        kwargs['monitors_ret'] = 'yyy'
        from time import sleep
        
        sleep(10)
        return kwargs


class frontendMonitorHandler(SocketHandler):
    """Event handler for frontend events of monitor class"""
    @staticmethod
    def handleClientSearch(sender, **extra):
        """Deliver result of client search"""
        SocketHandler.send_message(sender, **extra)

    @staticmethod
    def handleClientAnswer(sender, **extra):
        """Deliver data from client answer"""
        SocketHandler.send_message(sender, **extra)
