from emonitor.utils import Module
from emonitor.extensions import classes, db, babel
from .content_admin import getAdminContent, getAdminData
from .content_frontend import getFrontendContent, getFrontendData


class AlarmobjectsModule(Module):
    
    info = dict(area=['admin', 'frontend'], name='alarmobjects', path='alarmobjects', version='0.1')
    
    def __repr__(self):
        return "alarmobjects"
        
    def __init__(self, app):
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/alarmobjects/templates" % app.config.get('PROJECT_ROOT'))

        # create database tables
        from .alarmobject import AlarmObject
        classes.add('alarmobject', AlarmObject)
        db.create_all()

        # translations
        babel.gettext(u'module.alarmobjects')

    def getAdminContent(self, **params):
        return getAdminContent(self, **params)

    def getAdminData(self):
        return getAdminData(self)

    def getFrontendContent(self, params={}):
        return getFrontendContent(self, params)

    def getFrontendData(self):
        return getFrontendData(self)
