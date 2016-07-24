import os
import datetime
import time
import shutil
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
        events.addHandlerClass('file_added', 'emonitor.modules.textmod.TextmodModule', TextmodModule.handleEvent, ['in.path', 'in.filename', 'out.filename'])
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
        babel.gettext(u'emonitor.modules.textmod.TextmodModule')

    @staticmethod
    def handleEvent(eventname, **kwargs):
        """
        replace income filename with date as name to prevent exception in handler operation and move file in filesystem

        :param eventname: unused
        :param kwargs: all given parameters of current event chain
        :return: changed filename parameter, others unchanged
        """
        if 'time' not in kwargs:
            kwargs['time'] = []
        if 'incomepath' not in kwargs or 'filename' not in kwargs:
            kwargs['time'].append(u'textmod: missing parameters for textmod, nothing done.')
            return kwargs

        kwargs['time'].append(u'textmod: fix filenames.')
        stime = time.time()

        filename = "{}{}".format('{:%Y%m%d-%H%M%S}'.format(datetime.datetime.now()), os.path.splitext(kwargs.get('filename'))[-1])
        shutil.move('{}{}'.format(kwargs.get('incomepath'), kwargs.get('filename')), '{}{}'.format(kwargs.get('incomepath'), filename))
        kwargs['filename'] = filename
        t = time.time() - stime
        kwargs['time'].append(u'textmod: filename changed to "{}" done in {} sec.'.format(filename, t))
        return kwargs

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
