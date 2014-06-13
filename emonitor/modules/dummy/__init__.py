
from emonitor.utils import Module


class DummyModule(Module):
    info = {'area': ['admin'], 'name': 'dummymodule', 'path': 'dummymodule', 'version': '0.1'}

    def __repr__(self):
        return "dummymodule"
        
    def __init__(self, app):
        Module.__init__(self, app)
        
        self.adminsubnavigation.append('test')

    def getAdminContent(self, params={}):
        return "content of dummy module"