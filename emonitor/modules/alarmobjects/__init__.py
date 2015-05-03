from flask import send_from_directory, current_app
from emonitor.utils import Module
from emonitor.extensions import db, babel
from emonitor.modules.alarmobjects.content_admin import getAdminContent, getAdminData
from emonitor.modules.alarmobjects.content_frontend import getFrontendData
from emonitor.modules.alarmobjects.alarmobject import AlarmObject
from emonitor.modules.alarmobjects.alarmobjecttype import AlarmObjectType
from emonitor.modules.alarmobjects.alarmobjectfile import AlarmObjectFile


class AlarmobjectsModule(Module):
    """
    Definition of alarmobjects module with frontend and admin area
    """
    info = dict(area=['admin', 'frontend'], name='alarmobjects', path='alarmobjects', icon='fa-building', version='0.1')
    
    def __repr__(self):
        return "alarmobjects"
        
    def __init__(self, app):
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append(u"{}/emonitor/modules/alarmobjects/templates".format(app.config.get('PROJECT_ROOT')))

        # subnavigation
        self.adminsubnavigation = [(u'/admin/alarmobjects', u'module.alarmobjects.base'), (u'/admin/alarmobjects/types', u'module.alarmobjects.types'), (u'/admin/alarmobjects/fields', u'module.alarmobjects.fields')]

        # translations
        babel.gettext(u'module.alarmobjects')
        babel.gettext(u'module.alarmobjects.base')
        babel.gettext(u'module.alarmobjects.types')
        babel.gettext(u'module.alarmobjects.fields')

        @app.route('/alarmobjects/file/<path:filename>')  # filename = [id]-[filensme].ext
        def objectfile_static(filename):
            id, name = filename.split('-')
            alarmobjectfile = AlarmObjectFile.getFile(id=id, filename=name)
            return send_from_directory(u'{}alarmobjects/{}/'.format(current_app.config.get('PATH_DATA'), id), alarmobjectfile.filename)

    def checkDefinition(self):
        if AlarmObjectType.query.count() == 0:
            return Module.INITNEEDED
        return Module.CHECKOK

    def getAdminContent(self, **params):
        """
        Call *getAdminContent* of alarmobjects class

        :param params: send given parameters to :py:class:`emonitor.modules.alarmobjects.content_admin.getAdminContent`
        """
        return getAdminContent(self, **params)

    def getAdminData(self):
        """
        Call *getAdminData* of alarmobjects class
        """
        return getAdminData(self)

    def getFrontendData(self):
        """
        Call *getFrontendData* of alarmobjects class
        """
        return getFrontendData(self)
