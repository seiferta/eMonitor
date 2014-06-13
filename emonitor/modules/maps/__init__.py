from flask import send_from_directory
from emonitor.utils import Module
from emonitor.extensions import classes, db, babel
from emonitor.widget.monitorwidget import MonitorWidget
from .content_admin import getAdminContent, getAdminData
from .content_frontend import getFrontendContent, getFrontendData


class MapsModule(Module):
    info = {'area': ['admin', 'frontend', 'widget'], 'name': 'maps', 'path': 'maps', 'version': '0.1'}

    def __repr__(self):
        return "maps"

    def __init__(self, app):
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/maps/templates" % app.config.get('PROJECT_ROOT'))

        # create database tables
        from .map import Map
        classes.add('map', Map)
        db.create_all()

        self.widgets = [MonitorWidget('maps_map', size=(2, 2), template='widget.map.html')]

        # static folders
        @app.route('/maps/inc/<path:filename>')
        def maps_static(filename):
            return send_from_directory("%s/emonitor/modules/maps/inc/" % app.config.get('PROJECT_ROOT'), filename)

        # translations
        babel.gettext(u'module.maps')
        babel.gettext(u'maps_map')

    def frontendContent(self):
        return 1

    def getAdminContent(self, **params):
        return getAdminContent(self, **params)

    def getAdminData(self, params={}):
        return getAdminData(self, **params)

    def getFrontendContent(self, **params):
        return getFrontendContent(**params)

    def getFrontendData(self):
        return getFrontendData(self)