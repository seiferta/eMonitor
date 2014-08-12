from flask import send_from_directory
from emonitor.utils import Module
from emonitor.extensions import classes, db, babel
from .content_admin import getAdminContent, getAdminData
from emonitor.modules.settings import settings_utils


class SettingsModule(Module):
    info = {'area': ['admin'], 'name': 'settings', 'path': 'settings', 'version': '0.1'}
    
    def __repr__(self):
        return "settings"

    def __init__(self, app):
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/settings/templates" % app.config.get('PROJECT_ROOT'))

        # subnavigation
        self.adminsubnavigation = [('/admin/settings', 'settings.main'), ('/admin/settings/department', 'settings.department'), ('/admin/settings/cars', 'settings.cars'), ('/admin/settings/start', 'settings.start')]
       
        # create database tables
        from .settings import Settings
        from .department import Department
        classes.add('settings', Settings)
        classes.add('department', Department)
        db.create_all()
        
        # static folders
        @app.route('/settings/inc/<path:filename>')
        def settings_static(filename):
            return send_from_directory("%s/emonitor/modules/settings/inc/" % app.config.get('PROJECT_ROOT'), filename)
            
        # translations
        babel.gettext(u'module.settings')
        babel.gettext(u'settings.main')
        babel.gettext(u'settings.department')
        babel.gettext(u'settings.cars')
        babel.gettext(u'settings.start')

        babel.gettext(u'settings.pathtype.pathdone')
        babel.gettext(u'settings.pathtype.pathtmp')
        babel.gettext(u'settings.pathtype.pathdata')
        babel.gettext(u'settings.pathtype.pathincome')

    def getAdminContent(self, **params):
        return getAdminContent(self, **params)

    def getAdminData(self, **params):
        return getAdminData(self, **params)
