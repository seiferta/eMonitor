import re
from flask import send_from_directory
from emonitor.utils import Module
from emonitor.modules.settings.settings import Settings
from emonitor.extensions import classes, db, babel
from emonitor.modules.mapitems.content_admin import getAdminContent, getAdminData


class MapitemsModule(object, Module):
    info = dict(area=['admin'], name='mapitems', path='mapitems', icon='fa-bullseye', version='0.1')

    def __repr__(self):
        return "mapitems"

    def __init__(self, app):
        Module.__init__(self, app)

        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/mapitems/templates" % app.config.get('PROJECT_ROOT'))

        # create database tables
        from emonitor.modules.mapitems.mapitem import MapItem
        classes.add('mapitem', MapItem)
        db.create_all()

        # static folders
        @app.route('/mapitem/inc/<path:filename>')
        def mapitm_static(filename):
            return send_from_directory("%s/emonitor/modules/mapitem/inc/" % app.config.get('PROJECT_ROOT'), filename)

        # subnavigation
        self.updateAdminSubNavigation()

        # translations
        babel.gettext(u'module.mapitems')
        babel.gettext(u'module.mapitems.definition')
        babel.gettext(u'mapitems.definition')

    def updateAdminSubNavigation(self):
        self.adminsubnavigation = []
        for maptype in Settings.get('mapitemdefinition'):
            self.adminsubnavigation.append(('/admin/mapitems/%s' % maptype['name'], '%s' % maptype['name']))
        self.adminsubnavigation.append(('/admin/mapitems/definition', 'mapitems.definition'))

    def getHelp(self, area="frontend", name=""):  # frontend help template
        name = name.replace('help/', '').replace('/', '.')
        if not name.endswith('definition'):
            name = name.split('.')[0]
        name = re.sub(".\d+", "", name)
        return super(MapitemsModule, self).getHelp(area=area, name=name)

    def getAdminContent(self, **params):
        return getAdminContent(self, **params)

    def getAdminData(self,):
        return getAdminData(self)
