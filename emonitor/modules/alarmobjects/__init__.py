from emonitor.utils import Module
from emonitor.extensions import classes, db, babel
from .content_admin import getAdminContent, getAdminData
from .content_frontend import getFrontendData


class AlarmobjectsModule(Module):
    
    info = dict(area=['admin', 'frontend'], name='alarmobjects', path='alarmobjects', icon='fa-building', version='0.1')
    
    def __repr__(self):
        return "alarmobjects"
        
    def __init__(self, app):
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/alarmobjects/templates" % app.config.get('PROJECT_ROOT'))

        # subnavigation
        self.adminsubnavigation = [('/admin/alarmobjects', 'module.alarmobjects.base'), ('/admin/alarmobjects/types', 'module.alarmobjects.types')]

        # create database tables
        from .alarmobject import AlarmObject
        from .alarmobjecttype import AlarmObjectType
        classes.add('alarmobject', AlarmObject)
        classes.add('alarmobjecttype', AlarmObjectType)
        db.create_all()

        # translations
        babel.gettext(u'module.alarmobjects')
        babel.gettext(u'module.alarmobjects.base')
        babel.gettext(u'module.alarmobjects.types')

    def checkDefinition(self):
        if db.session.query(classes.get('alarmobjecttype')).count() == 0:
            return Module.INITNEEDED
        return Module.CHECKOK

    def getAdminContent(self, **params):
        return getAdminContent(self, **params)

    def getAdminData(self):
        return getAdminData(self)

    def getFrontendData(self):
        return getFrontendData(self)
