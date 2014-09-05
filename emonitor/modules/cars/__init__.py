from emonitor.utils import Module
from emonitor.widget.monitorwidget import MonitorWidget
from emonitor.extensions import classes, db, babel
from emonitor.modules.cars.content_admin import getAdminContent
from emonitor.modules.cars.content_frontend import getFrontendData


class CarsModule(Module):
    info = dict(area=['admin', 'frontend', 'widget'], name='cars', path='cars', icon='fa-truck', version='0.1')

    def __repr__(self):
        return "cars"

    def __init__(self, app):
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/cars/templates" % app.config.get('PROJECT_ROOT'))
        
        # subnavigation
        self.updateAdminSubNavigation()
       
        self.widgets = [MonitorWidget('cars', size=(1, 1), template='widget.cars.html')]

        # create database tables
        from .car import Car
        classes.add('car', Car)
        db.create_all()

        # translations
        babel.gettext(u'module.cars')
        babel.gettext(u'cars')

    def updateAdminSubNavigation(self):
        from emonitor.modules.settings.department import Department
        self.adminsubnavigation = []
        for dep in Department.getDepartments():
            self.adminsubnavigation.append(('/admin/cars/%s' % dep.id, dep.name))
        
    def getAdminContent(self, **params):
        return getAdminContent(self, **params)

    def getAdminData(self, params={}):
        return ""

    def getFrontendData(self):
        return getFrontendData(self)
