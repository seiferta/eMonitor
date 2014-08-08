from emonitor.utils import Module
from emonitor.extensions import classes, db, babel
from emonitor.modules.events.content_admin import getAdminContent, getAdminData


class EventsModule(Module):
    info = {'area': ['admin'], 'name':'events', 'path':'events', 'version': '0.1'}
    
    def __repr__(self):
        return "events"
    
    def __init__(self, app):
        Module.__init__(self, app)

        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/events/templates" % app.config.get('PROJECT_ROOT'))

        # create database tables
        from .eventhandler import Eventhandler
        classes.add('eventhandler', Eventhandler)
        db.create_all()
        
        # translations
        babel.gettext(u'module.events')
        
    def getAdminContent(self, **params):
        return getAdminContent(self, **params)
            
    def getAdminData(self, **params):
        return getAdminData(self, **params)
