from flask import send_from_directory
from emonitor.utils import Module
from emonitor.extensions import babel, events
from emonitor.modules.printers.printers import Printers
from emonitor.modules.printers.content_frontend import getFrontendContent, getFrontendData
from emonitor.modules.printers.content_admin import getAdminContent, getAdminData


class PrintersModule(Module):
    """
    Definition of printers module with admin area
    """
    info = dict(area=['admin'], name='printers', path='printers', icon='fa-print', version='0.1')

    def __repr__(self):
        return "printer"

    def __init__(self, app):
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append(u"{}/emonitor/modules/printers/templates".format(app.config.get('PROJECT_ROOT')))

        # add events and handler
        events.addHandlerClass('*', 'emonitor.modules.printers.printers.Printers', Printers.handleEvent, ['in.printerid'])

        # subnavigation
        self.adminsubnavigation = [('/admin/printers', 'printers.main'), ('/admin/printers/settings', 'module.printers.settings')]

        # static folders
        @app.route('/printer/inc/<path:filename>')
        def printer_static(filename):
            return send_from_directory(u"{}/emonitor/modules/printers/inc/".format(app.config.get('PROJECT_ROOT')), filename)

        # translations
        babel.gettext(u'module.printers')
        babel.gettext(u'printers.main')
        babel.gettext(u'module.printers.settings')
        babel.gettext(u'emonitor.modules.printers.printers.Printers')
        babel.gettext(u'template.alarm_sum')
        babel.gettext(u'template.alarm_original')

    def getAdminContent(self, **params):
        """
        Call *getAdminContent* of printers class

        :param params: send given parameters to :py:class:`emonitor.modules.printers.content_admin.getAdminContent`
        """
        return getAdminContent(self, **params)

    def getAdminData(self, *params):
        """
        Call *getAdminData* method of monitors class and return values

        :return: return result of method
        """
        return getAdminData(self)

    def getFrontendContent(self, **params):
        """UNUSED"""
        return getFrontendContent(self, **params)

    def getFrontendData(self):
        """UNUSED"""
        return getFrontendData(self)
