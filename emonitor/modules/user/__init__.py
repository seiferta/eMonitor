from flask import render_template
from emonitor.utils import Module
from emonitor.extensions import babel


class UserModule(Module):
    info = {'area': ['admin'], 'name': 'usermodule', 'path': 'users', 'version': '0.1'}
    
    def __repr__(self):
        return "usermodule"

    def __init__(self, app):
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/user/templates" % app.config.get('PROJECT_ROOT'))
        
        babel.gettext(u'module.usermodule')

    def getAdminContent(self, **params):
        return render_template('admin.user.html', **params)
