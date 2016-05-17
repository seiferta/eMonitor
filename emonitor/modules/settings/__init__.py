import mimetypes
from flask import send_from_directory
from emonitor.utils import Module
from emonitor.extensions import babel, db
from emonitor.widget.monitorwidget import MonitorWidget
from emonitor.modules.settings.content_admin import getAdminContent, getAdminData
from emonitor.modules.settings import settings_utils
from emonitor.modules.settings.department import Department
from emonitor.modules.settings.settings import Settings


class SettingsModule(Module):
    """
    Definition of settings module with admin area
    """
    info = dict(area=['admin', 'widget'], name='settings', path='settings', icon='fa-gears', version='0.1')

    def __repr__(self):
        return "settings"

    def __init__(self, app):
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/settings/templates" % app.config.get('PROJECT_ROOT'))

        self.widgets = [CrestWidget('departmentcrest')]

        # subnavigation
        self.adminsubnavigation = [('/admin/settings', 'settings.main'), ('/admin/settings/department', 'module.settings.department'), ('/admin/settings/cars', 'module.settings.cars'), ('/admin/settings/communication', 'module.settings.communication'), ('/admin/settings/start', 'module.settings.start')]

        # static folders
        @app.route('/settings/inc/<path:filename>')
        def settings_static(filename):
            return send_from_directory("%s/emonitor/modules/settings/inc/" % app.config.get('PROJECT_ROOT'), filename)
            
        # translations
        babel.gettext(u'module.settings')
        babel.gettext(u'settings.main')
        babel.gettext(u'module.settings.department')
        babel.gettext(u'module.settings.cars')
        babel.gettext(u'module.settings.communication')
        babel.gettext(u'module.settings.start')

        babel.gettext(u'settings.pathtype.pathdone')
        babel.gettext(u'settings.pathtype.pathtmp')
        babel.gettext(u'settings.pathtype.pathdata')
        babel.gettext(u'settings.pathtype.pathincome')

        babel.gettext(u'departmentcrest')
        babel.gettext(u'telegram.default.welcomemsg')

        # add default values
        if Settings.query.count() == 0:  # add default values
            db.session.add(Settings.set('defaultZoom', 15))
            db.session.add(Settings.set('startLat', ''))
            db.session.add(Settings.set('startLng', ''))
            db.session.add(Settings.set('homeLat', ''))
            db.session.add(Settings.set('homeLng', ''))
            db.session.add(Settings.set('alarms.evalfields', '_bab_\r\n_train_\r\n_street_\r\n_default_city_\r\n_interchange_\r\n_kilometer_\r\n_bma_\r\n_bma_main_\r\n_bma_key_\r\n_train_identifier_'))
            db.session.add(Settings('cartypes', "- [car, '#ffffff']\n"))
            db.session.commit()

    def checkDefinition(self):
        if len(Department.getDepartments()) == 0:
            return Module.INITNEEDED
        return Module.CHECKOK

    def fixDefinition(self, id):
        pass

    def getAdminContent(self, **params):
        """
        Call *getAdminContent* of settings class

        :param params: send given parameters to :py:class:`emonitor.modules.settings.content_admin.getAdminContent`
        """
        return getAdminContent(self, **params)

    def getAdminData(self, **params):
        """
        Call *getAdminData* method of settings class and return values

        :return: return result of method
        """
        return getAdminData(self, **params)


class CrestWidget(MonitorWidget):
    """Car widget for alarms"""
    template = 'widget.department_crest.html'
    size = (1, 2)

    def addParameters(self, **kwargs):
        mimetypes.init()
        dep = Department.getDefaultDepartment()
        if kwargs.get('alarm'):
            try:
                dep = kwargs.get('alarm').city.department
                print "alarmdepaprtment", dep.name
            except:
                pass
        if dep and 'logo' in dep.attributes:
            kwargs.update(crest=dep.getLogoStream(), mime=mimetypes.guess_type(dep.attributes['logo'])[0])
        self.params.update(kwargs)
