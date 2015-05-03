from emonitor.utils import Module
from emonitor.extensions import babel
from emonitor.modules.events.content_admin import getAdminContent, getAdminData
from emonitor.modules.events.eventhandler import Eventhandler


class EventsModule(Module):
    """
    Definition of event module with frontend, admin and widget area
    """
    info = dict(area=['admin'], name='events', path='events', icon='fa-magic', version='0.1')
    
    def __repr__(self):
        return "events"
    
    def __init__(self, app):
        """
        Add specific parameters and configuration to app object

        :param app: flask wsgi application
        """
        Module.__init__(self, app)

        # add template path
        app.jinja_loader.searchpath.append(u"{}/emonitor/modules/events/templates".format(app.config.get('PROJECT_ROOT')))

        # translations
        babel.gettext(u'module.events')

    def checkDefinition(self):
        if Eventhandler.query.count() == 0:
            return Module.INITNEEDED
        return Module.CHECKOK
        
    def getAdminContent(self, **params):
        """
        Call *getAdminContent* of events class

        :param params: send given parameters to :py:class:`emonitor.modules.events.content_admin.getAdminContent`
        """
        return getAdminContent(self, **params)

    def getAdminData(self, **params):
        """
        Call *getAdminData* method of events class and return values

        :return: return result of method
        """
        return getAdminData(self, **params)
