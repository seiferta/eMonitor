from flask import send_from_directory, current_app
from emonitor.utils import Module
from emonitor.extensions import classes, db, babel
from .content_admin import getAdminContent, getAdminData
from .content_frontend import getFrontendData


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
        app.jinja_loader.searchpath.append("%s/emonitor/modules/alarmobjects/templates" % app.config.get('PROJECT_ROOT'))

        # subnavigation
        self.adminsubnavigation = [('/admin/alarmobjects', 'module.alarmobjects.base'), ('/admin/alarmobjects/types', 'module.alarmobjects.types'), ('/admin/alarmobjects/fields', 'module.alarmobjects.fields')]

        # create database tables
        from .alarmobject import AlarmObject
        from .alarmobjecttype import AlarmObjectType
        from .alarmobjectfile import AlarmObjectFile
        classes.add('alarmobject', AlarmObject)
        classes.add('alarmobjecttype', AlarmObjectType)
        classes.add('alarmobjectfile', AlarmObjectFile)
        db.create_all()

        # translations
        babel.gettext(u'module.alarmobjects')
        babel.gettext(u'module.alarmobjects.base')
        babel.gettext(u'module.alarmobjects.types')
        babel.gettext(u'module.alarmobjects.fields')

        @app.route('/alarmobjects/file/<path:filename>')  # filename = [id]-[filensme].ext
        def objectfile_static(filename):
            id, name = filename.split('-')
            alarmobjectfile = classes.get('alarmobjectfile').getFile(id=id, filename=name)
            fpath = '%salarmobjects/%s/' % (current_app.config.get('PATH_DATA'), id)
            return send_from_directory(fpath, alarmobjectfile.filename)

    def checkDefinition(self):
        if db.session.query(classes.get('alarmobjecttype')).count() == 0:
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
