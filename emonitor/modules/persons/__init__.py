import logging
import re
from emonitor.utils import Module
from emonitor.extensions import babel
from emonitor.modules.persons.content_admin import getAdminContent, getAdminData

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


class PersonsModule(object, Module):
    """
    Definition of persons module with admin
    """
    info = dict(area=['admin'], name='persons', path='persons', icon='fa-users', version='0.1')

    def __repr__(self):
        return "persons"

    def __init__(self, app):
        """
        Add specific parameters and configuration to app object

        :param app: flask wsgi application
        """
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("{}/emonitor/modules/persons/templates".format(app.config.get('PROJECT_ROOT')))

        # subnavigation
        self.updateAdminSubNavigation()

        # create database tables
        from emonitor.modules.persons.persons import Person

        # eventhandlers

        # signals and handlers

        from emonitor.modules.persons.message_birthday import BirthdayWidget
        from emonitor.modules.messages import addMessageType
        addMessageType(BirthdayWidget('message_birthday'))

        # translations
        babel.gettext(u'module.persons')
        babel.gettext(u'module.persons.0')
        babel.gettext(u'persons.upload.states-1')
        babel.gettext(u'persons.upload.states0')
        babel.gettext(u'persons.upload.states1')
        babel.gettext(u'birthday')

    def updateAdminSubNavigation(self):
        """
        Add submenu entries for admin area
        """
        from emonitor.modules.settings.department import Department
        self.adminsubnavigation = []
        for dep in Department.getDepartments():
            self.adminsubnavigation.append(('/admin/persons/%s' % dep.id, dep.name))
        self.adminsubnavigation.append(('/admin/persons/0', babel.gettext('admin.persons.edit...')))

    def getHelp(self, area="frontend", name=""):  # frontend help template
        name = name.replace('help/', '').replace('/', '.')
        if not name.endswith('.0'):
            name = re.sub(".\d+", "", name)
        return super(PersonsModule, self).getHelp(area=area, name=name)

    def frontendContent(self):
        return 1

    def getAdminContent(self, **params):
        """
        Call *getAdminContent* of alarms class

        :param params: send given parameters to :py:class:`emonitor.modules.alarms.content_admin.getAdminContent`
        """
        return getAdminContent(self, **params)

    def getAdminData(self):
        """
        Call *getAdminData* method of alarms class and return values

        :return: return result of method
        """
        return getAdminData(self)
