from flask import send_from_directory
from emonitor.modules import Module
from emonitor.extensions import babel, classes, db, events
from .content_admin import getAdminContent, getAdminData


class PrintersModule(Module):
    info = {'area': ['admin'], 'name': 'printer', 'path': 'printers', 'version': '0.1'}

    def __repr__(self):
        return "printer"

    def __init__(self, app):
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/printers/templates" % app.config.get('PROJECT_ROOT'))

        # create database tables
        from .printers import Printers
        classes.add('printer', Printers)
        db.create_all()

        # add events and handler
        events.addHandlerClass('*', 'emonitor.modules.printers.printers.Printers', Printers.handleEvent, ['in.printerid'])

        # subnavigation
        self.adminsubnavigation = [('/admin/printers', 'printers.main'), ('/admin/printers/settings', 'printers.settings')]

        # static folders
        @app.route('/printer/inc/<path:filename>')
        def printer_static(filename):
            return send_from_directory("%s/emonitor/modules/printer/inc/" % app.config.get('PROJECT_ROOT'), filename)

        # translations
        babel.gettext(u'module.printer')
        babel.gettext(u'printers.main')
        babel.gettext(u'printers.settings')
        babel.gettext(u'emonitor.modules.printers.printers.Printers')
        babel.gettext(u'template.alarm_sum')
        babel.gettext(u'template.alarm_original')

    def getAdminContent(self, **params):
        return getAdminContent(self, **params)

    def getAdminData(self, params={}):
        return getAdminData(self, params)
