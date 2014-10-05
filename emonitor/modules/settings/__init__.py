from flask import send_from_directory
from emonitor.utils import Module
from emonitor.extensions import classes, db, babel
from .content_admin import getAdminContent, getAdminData
from emonitor.modules.settings import settings_utils


class SettingsModule(Module):
    info = dict(area=['admin'], name='settings', path='settings', icon='fa-gears', version='0.1')

    def __repr__(self):
        return "settings"

    def __init__(self, app):
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/settings/templates" % app.config.get('PROJECT_ROOT'))

        # subnavigation
        self.adminsubnavigation = [('/admin/settings', 'settings.main'), ('/admin/settings/department', 'module.settings.department'), ('/admin/settings/cars', 'module.settings.cars'), ('/admin/settings/start', 'module.settings.start')]
       
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
        babel.gettext(u'module.settings.department')
        babel.gettext(u'module.settings.cars')
        babel.gettext(u'module.settings.start')

        babel.gettext(u'settings.pathtype.pathdone')
        babel.gettext(u'settings.pathtype.pathtmp')
        babel.gettext(u'settings.pathtype.pathdata')
        babel.gettext(u'settings.pathtype.pathincome')

        # add default values
        if db.session.query(Settings).count() == 0:  # add default values
            db.session.add(Settings.set('defaultZoom', 15))
            db.session.add(Settings.set('startLat', ''))
            db.session.add(Settings.set('startLng', ''))
            db.session.add(Settings.set('homeLat', ''))
            db.session.add(Settings.set('homeLng', ''))
            db.session.add(Settings.set('alarms.evalfields', '_bab_\r\n_train_\r\n_street_\r\n_default_city_\r\n_interchange_\r\n_kilometer_\r\n_bma_\r\n_bma_main_\r\n_bma_key_\r\n_train_identifier_'))
            db.session.add(Settings.set('cartypes', ['car', '#ffffff']))
            db.session.commit()

    def checkDefinition(self):
        if len(classes.get('department').getDepartments()) == 0:
            return Module.INITNEEDED
        return Module.CHECKOK

    def fixDefinition(self, id):
        pass

    def getAdminContent(self, **params):
        return getAdminContent(self, **params)

    def getAdminData(self, **params):
        return getAdminData(self, **params)
