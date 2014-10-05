import re
from flask import send_from_directory
from emonitor.sockethandler import SocketHandler
from emonitor.utils import Module
from emonitor.widget.monitorwidget import MonitorWidget
from emonitor.extensions import classes, db, babel, signal

from.city import City
from.street import Street
from .content_admin import getAdminContent, getAdminData
from .content_frontend import getFrontendData


class StreetsModule(object, Module):
    info = dict(area=['admin', 'frontend', 'widget'], name='streets', path='streets', icon='fa-road', version='0.1')
    
    def __repr__(self):
        return "streets"

    def __init__(self, app):
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/streets/templates" % app.config.get('PROJECT_ROOT'))

        # create database tables
        from .street import Street
        from .city import City
        from .housenumber import Housenumber
        classes.add('city', City)
        classes.add('housenumber', Housenumber)
        classes.add('street', Street)
        db.create_all()

        # subnavigation
        self.updateAdminSubNavigation()
        self.widgets = [MonitorWidget('streets_street', size=(2, 1), template='widget.street.html')]

        signal.addSignal('housenumber', 'osm')
        signal.connect('housenumber', 'osm', adminHousenumberHandler.handleOSMChanged)
        signal.connect('housenumber', 'osmdone', adminHousenumberHandler.handleOSMDone)

        # static folders
        @app.route('/streets/inc/<path:filename>')
        def streets_static(filename):
            return send_from_directory("%s/emonitor/modules/streets/inc/" % app.config.get('PROJECT_ROOT'), filename)
            
        # translations
        babel.gettext(u'module.streets')
        babel.gettext(u'module.streets.0')
        babel.gettext(u'streets_street')  # widget name

    def updateAdminSubNavigation(self):
        from .city import City
        self.adminsubnavigation = []
        for c in City.getCities():
            self.adminsubnavigation.append(('/admin/streets/%s' % c.id, c.name))
        self.adminsubnavigation.append(('/admin/streets/0', babel.gettext('admin.streets.cities.edit...')))

    def getHelp(self, area="frontend", name=""):  # frontend help template
        name = name.replace('help/', '').replace('/', '.')
        if not name.endswith('.0'):
            name = re.sub(".\d+", "", name)
        return super(StreetsModule, self).getHelp(area=area, name=name)

   # @cache.cached(timeout=8000, key_prefix='streets')
    #def getFrontendContent(self, params={}):
    #    return getFrontendContent(self, params=params)

    def checkDefinition(self):
        if db.session.query(classes.get('city')).count() == 0:
            return Module.INITNEEDED
        return Module.CHECKOK
        
    def getFrontendData(self):
        return getFrontendData(self)

    def getAdminContent(self, **params):
        return getAdminContent(self, **params)

    def getAdminData(self):
        return getAdminData(self)


class adminHousenumberHandler(SocketHandler):
    @staticmethod
    def handleOSMChanged(sender, **extra):
        SocketHandler.send_message(sender, **extra)

    @staticmethod
    def handleOSMDone(sender, **extra):
        SocketHandler.send_message(sender, **extra)
