from flask import send_from_directory
from emonitor.utils import Module
from emonitor.extensions import db, babel, signal
from emonitor.modules.maps.content_admin import getAdminContent, getAdminData
from emonitor.modules.maps.content_frontend import getFrontendContent, getFrontendData
from emonitor.modules.maps.map import Map, MapWidget
from emonitor.modules.maps.map_utils import adminMapHandler


class MapsModule(Module):
    """
    Definition of maps module with frontend, admin and widget area
    """
    info = dict(area=['admin', 'frontend', 'widget'], name='maps', path='maps', icon='fa-globe', version='0.1')

    def __repr__(self):
        return "maps"

    def __init__(self, app):
        """
        Add specific parameters and configuration to app object

        :param app: flask wsgi application
        """
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/maps/templates" % app.config.get('PROJECT_ROOT'))

        # subnavigation
        self.adminsubnavigation = [('/admin/maps', 'maps.base'), ('/admin/maps/position', 'module.maps.position')]

        self.widgets = [MapWidget('maps_map')]

        # signals and handlers
        signal.connect('map', 'tiledownloadstart', adminMapHandler.handleMapDownloadStart)
        signal.connect('map', 'tiledownloadstop', adminMapHandler.handleMapDownloadStop)
        signal.connect('map', 'tiledownloaddone', adminMapHandler.handleMapDownloadDone)
        signal.connect('map', 'tiledownloadprogress', adminMapHandler.handleMapDownloadProgress)

        # static folders
        @app.route('/maps/inc/<path:filename>')
        def maps_static(filename):
            return send_from_directory("%s/emonitor/modules/maps/inc/" % app.config.get('PROJECT_ROOT'), filename)

        # translations
        babel.gettext(u'module.maps')
        babel.gettext(u'maps_map')
        babel.gettext(u'maps.base')
        babel.gettext(u'module.maps.position')

    def checkDefinition(self):
        if Map.query.count() == 0:
            return Module.INITNEEDED
        return Module.CHECKOK

    def fixDefinition(self, id):
        if id == 1:  # add default values
            if Map.query.count() == 0:  # add default map
                db.session.add(Map('Bing (online)', '', maptype=2, tileserver="//ak.t2.tiles.virtualearth.net/tiles/a{q}?g=1236", default=1))
                db.session.commit()

    def frontendContent(self):
        return 1

    def getAdminContent(self, **params):
        """
        Call *getAdminContent* of maps class

        :param params: send given parameters to :py:class:`emonitor.modules.maps.content_admin.getAdminContent`
        """
        return getAdminContent(self, **params)

    def getAdminData(self, **params):
        """
        Call *getAdminData* method of maps class and return values

        :return: return result of method
        """
        return getAdminData(self, **params)

    def getFrontendContent(self, **params):
        """
        Call *getFrontendContent* of maps class

        :param params: send given parameters to :py:class:`emonitor.modules.maps.content_frontend.getFrontendContent`
        """
        return getFrontendContent(**params)

    def getFrontendData(self):
        """
        Call *getFrontendData* of maps class
        """
        return getFrontendData(self)
