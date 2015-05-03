from emonitor.utils import Module
from emonitor.extensions import events, babel
from .content_admin import getAdminContent, getAdminData


class TextmodModule(Module):
    """
    Definition of textmod module with admin area
    """
    info = dict(area=['admin'], name='textmod', path='textmod', icon='fa-text-width', version='0.1')
    
    def __repr__(self):
        return "textmod"

    def __init__(self, app):
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/textmod/templates" % app.config.get('PROJECT_ROOT'))

        # subnavigation
        self.adminsubnavigation = [('/admin/textmod', 'module.textmod.replace'), ('/admin/textmod/ocr', 'module.textmod.ocr'), ('/admin/textmod/ocrcustom', 'module.textmod.ocrcustom'), ('/admin/textmod/convert', 'module.textmod.convert')]
        
        # create database tables
        from .replace import Replace
        from .ocr import Ocr

        # eventhandlers
        events.addHandlerClass('file_added', 'emonitor.modules.textmod.ocr.Ocr', Ocr.handleEvent, ['in.path', 'in.filename', 'out.text'])
        events.addHandlerClass('file_added', 'emonitor.modules.textmod.replace.Replace', Replace.handleEvent, ['in.text', 'out.text'])
        
        # translations
        babel.gettext(u'module.textmod')
        babel.gettext(u'module.textmod.replace')
        babel.gettext(u'module.textmod.ocr')
        babel.gettext(u'module.textmod.ocrcustom')
        babel.gettext(u'module.textmod.convert')
        babel.gettext(u'emonitor.modules.textmod.ocr.Ocr')
        babel.gettext(u'emonitor.modules.textmod.replace.Replace')

    def getAdminContent(self, **params):
        """
        Call *getAdminContent* of testmod class

        :param params: send given parameters to :py:class:`emonitor.modules.textmod.content_admin.getAdminContent`
        """
        return getAdminContent(self, **params)

    def getAdminData(self):
        """
        Call *getAdminData* method of textmod class and return values

        :return: return result of method
        """
        return getAdminData(self)
