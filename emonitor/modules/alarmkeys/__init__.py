from flask import send_from_directory
from emonitor.utils import Module
from emonitor.extensions import db, classes, babel

from emonitor.modules.alarmkeys.content_admin import getAdminContent, getAdminData
from emonitor.modules.alarmkeys.content_frontend import getFrontendData


class AlarmkeysModule(Module):
    info = dict(area=['admin', 'frontend'], name='alarmkeys', path='alarmkeys', version='0.1')
    
    def __repr__(self):
        return "alarmkeys"
    
    def __init__(self, app):
        Module.__init__(self, app)
        
        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/alarmkeys/templates" % app.config.get('PROJECT_ROOT'))

        # subnavigation
        self.updateAdminSubNavigation()

        # create database tables
        from alarmkey import Alarmkey
        from alarmkeycar import AlarmkeyCars
        classes.add('alarmkey', Alarmkey)
        classes.add('alarmkeycar', AlarmkeyCars)
        db.create_all()
        
        # subnavigation
        self.updateAdminSubNavigation()
        
        # static folders
        @app.route('/alarmkeys/inc/<path:filename>')
        def alarmkeys_static(filename):
            return send_from_directory("%s/emonitor/modules/alarmkeys/inc/" % app.config.get('PROJECT_ROOT'), filename)
            
        babel.gettext(u'module.alarmkeys')
        babel.gettext(u'alarmkeys.upload.states0')
        babel.gettext(u'alarmkeys.upload.states1')
        babel.gettext(u'alarmkeys.upload.states-1')

    def updateAdminSubNavigation(self):
        from emonitor.modules.settings.department import Department
        self.adminsubnavigation = []
        for dep in Department.getDepartments():
            self.adminsubnavigation.append(('/admin/alarmkeys/%s' % dep.id, dep.name))
        
    def getAdminContent(self, **params):
        return getAdminContent(self, **params)
        
    def getAdminData(self):
        return getAdminData(self)
        
    def getFrontendData(self, params={}):
        return getFrontendData(params, params)
