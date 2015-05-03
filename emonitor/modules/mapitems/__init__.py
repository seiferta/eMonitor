import re
from flask import send_from_directory
from emonitor.utils import Module
from emonitor.extensions import babel
from emonitor.modules.mapitems.mapitem import MapItem
from emonitor.modules.mapitems.content_admin import getAdminContent, getAdminData
from emonitor.modules.settings.settings import Settings


class MapitemsModule(object, Module):
    """
    Definition of mapitems module with admin area
    """
    info = dict(area=['admin'], name='mapitems', path='mapitems', icon='fa-bullseye', version='0.1')

    def __repr__(self):
        return "mapitems"

    def __init__(self, app):
        """
        Add specific parameters and configuration to app object

        :param app: flask wsgi application
        """
        Module.__init__(self, app)

        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/mapitems/templates" % app.config.get('PROJECT_ROOT'))

        # static folders
        @app.route('/mapitem/inc/<path:filename>')
        def mapitm_static(filename):
            return send_from_directory("%s/emonitor/modules/mapitem/inc/" % app.config.get('PROJECT_ROOT'), filename)

        # translations
        babel.gettext(u'module.mapitems')
        babel.gettext(u'module.mapitems.definition')
        babel.gettext(u'mapitems.definition')

    def updateAdminSubNavigation(self):
        """
        Add submenu entries for admin area
        """
        from sqlalchemy.exc import OperationalError
        self.adminsubnavigation = []
        try:
            for maptype in Settings.get('mapitemdefinition'):
                self.adminsubnavigation.append(('/admin/mapitems/%s' % maptype['name'], '%s' % maptype['name']))
        except OperationalError:
            pass
        self.adminsubnavigation.append(('/admin/mapitems/definition', 'mapitems.definition'))

    def getHelp(self, area="frontend", name=""):
        """
        Get special html content for mapitems module

        :param optional area: *frontend*, *admin*
        :param name: name of help template
        """
        name = name.replace('help/', '').replace('/', '.')
        if not name.endswith('definition'):
            name = name.split('.')[0]
        name = re.sub(".\d+", "", name)
        return super(MapitemsModule, self).getHelp(area=area, name=name)

    def getAdminContent(self, **params):
        """
        Call *getAdminContent* of mapitems class

        :param params: send given parameters to :py:class:`emonitor.modules.mapitems.content_admin.getAdminContent`
        """
        self.updateAdminSubNavigation()
        return getAdminContent(self, **params)

    def getAdminData(self):
        """
        Call *getAdminData* method of mapitems class and return values

        :return: return result of method
        """
        return getAdminData(self)
