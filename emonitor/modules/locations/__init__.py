from emonitor.utils import Module
from emonitor.extensions import babel
from .content_frontend import getFrontendContent, getFrontendData


class LocationsModule(Module):
    info = dict(area=['frontend'], name='locations', path='locations', icon='fa-code-fork', version='0.1')

    def __repr__(self):
        return "locations"

    def __init__(self, app):
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/locations/templates" % app.config.get('PROJECT_ROOT'))

        # translations
        babel.gettext(u'module.locations')

    def frontendContent(self):
        return 1

    def getFrontendContent(self, **params):
        return getFrontendContent(**params)

    def getFrontendData(self):
        return getFrontendData(self)
