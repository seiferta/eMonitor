from emonitor.utils import Module
from emonitor.extensions import babel
from .content_admin import getAdminContent


class UserModule(Module):
    info = dict(area=['admin'], name='usermodule', path='users', icon='fa-users', version='0.1')
    
    def __repr__(self):
        return "usermodule"

    def __init__(self, app):
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/user/templates" % app.config.get('PROJECT_ROOT'))
        
        babel.gettext(u'module.usermodule')
        babel.gettext(u'userlevel.notset')
        babel.gettext(u'userlevel.admin')
        babel.gettext(u'userlevel.user')

    def getAdminContent(self, **params):
        return getAdminContent(self, **params)