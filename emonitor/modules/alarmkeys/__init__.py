from flask import send_from_directory
from emonitor.utils import Module
from emonitor.extensions import babel
from emonitor.modules.settings.department import Department
from emonitor.modules.alarmkeys.content_admin import getAdminContent, getAdminData
from emonitor.modules.alarmkeys.content_frontend import getFrontendData


class AlarmkeysModule(Module):
    """
    Definition of alarmkeys module with frontend and admin area
    """
    info = dict(area=['admin', 'frontend'], name='alarmkeys', path='alarmkeys', icon='fa-list-ol', version='0.1')
    
    def __repr__(self):
        return "alarmkeys"
    
    def __init__(self, app):
        """
        Add specific parameters and configuration to app object

        :param app: flask wsgi application
        """
        Module.__init__(self, app)
        
        # add template path
        app.jinja_loader.searchpath.append(u"{}/emonitor/modules/alarmkeys/templates".format(app.config.get('PROJECT_ROOT')))

        # create database tables
        from alarmkey import Alarmkey
        from alarmkeycar import AlarmkeyCars

        # static folders
        @app.route('/alarmkeys/inc/<path:filename>')
        def alarmkeys_static(filename):
            return send_from_directory(u"{}/emonitor/modules/alarmkeys/inc/".format(app.config.get('PROJECT_ROOT')), filename)
            
        babel.gettext(u'module.alarmkeys')
        babel.gettext(u'alarmkeys.upload.states0')
        babel.gettext(u'alarmkeys.upload.states1')
        babel.gettext(u'alarmkeys.upload.states-1')

    def updateAdminSubNavigation(self):
        """
        Add subnavigation for admin area with sections for alarmkey module
        """
        self.adminsubnavigation = []
        for dep in Department.getDepartments():
            self.adminsubnavigation.append(('/admin/alarmkeys/%s' % dep.id, dep.name))
        self.adminsubnavigation.append(('/admin/alarmkeys/0', babel.gettext('admin.alarmkeys.sets.edit...')))
        
    def getAdminContent(self, **params):
        """
        Call *getAdminContent* of alarmkeys class

        :param params: send given parameters to :py:func:`emonitor.modules.alarmkeys.content_admin.getAdminContent`
        """
        self.updateAdminSubNavigation()
        return getAdminContent(self, **params)
        
    def getAdminData(self):
        """
        Call *getAdminData* method of alarmkeys class and return values

        :return: return result of method
        """
        return getAdminData(self)
        
    def getFrontendData(self, **params):
        """
        Call *getFrontendData* of alarmkeys class

        :param params: send given parameters to :py:func:`emonitor.modules.alarmkeys.content_admin.getFrontendData`
        :return: return result of method
        """
        return getFrontendData(params, params)
