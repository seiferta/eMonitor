import os
import codecs
import logging
import re
from flask import current_app, Markup
from math import ceil
from xhtml2pdf import pisa
from StringIO import StringIO
from emonitor.socketserver import SocketHandler

logger = logging.getLogger('xhtml2pdf')
logger.setLevel(logging.ERROR)


class Classes:
    """Load all modules from module folder in global classes cache"""
    classes = {}
    dependencies = {}
    classcache = {}

    def __init__(self):
        pass

    @staticmethod
    def get(classname):
        """
        Get class object from class cache

        :param classname: name of class as string

        :return: class object if classname is defined in classes cache
        """
        if classname in Classes.classes:
            # cache classes
            if classname not in Classes.classcache:  # init class once
                Classes.classcache[classname] = Classes.classes[classname]
            return Classes.classcache[classname]
            # classcache end
            # return self.classes[classname]() # deliver new instance
        return None
        
    @staticmethod
    def add(classname, cls):
        """
        Add class to class cache

        :param classname: name of class as string
        :param cls: class object
        """
        Classes.classes[classname] = cls
    
    @staticmethod
    def addDependency(classname, dependon):
        """
        Add dependency for class: Each class can depend on other classes. Be sure all dependencies are present.

        :param classname: name of class as string
        :param dependon: name of class as string
        """
        if dependon not in Classes.dependencies:
            Classes.dependencies[dependon] = []
        Classes.dependencies[dependon].append(classname)
        
    @staticmethod
    def changes(classname):
        """
        Inform all classes of changes in class

        :param classname: name of changing class as string
        """
        if classname in Classes.dependencies:
            for cls in Classes.dependencies[classname]:
                if hasattr(Classes.classes[cls], 'dependencyChanged'):
                    Classes.classes[cls]().dependencyChanged(classname)


class Module:
    """
    Skeleton class for modules
    """

    CHECKOK = 0
    """configuration okay"""
    INITNEEDED = 1
    """basic configuration needed"""

    info = {}
    helppath = ""
    
    def __repr__(self):
        return Module.info['name']
    
    def __init__(self, app):
        self.app = app
        self.widgets = []
        self.adminsubnavigation = []
        self.dependency = []  # modulenames with dependency, if module data updated, alert
        self.signalHandler = SocketHandler
    
    @property
    def getName(self):
        try:
            return Module.info['name']
        except:
            return ""

    @property
    def getPath(self):
        return Module.info['path']

    def hasHelp(self, area="frontend"):
        """
        Test for online help of given area

        :param optional area: *frontend*, *admin*
        :return: *1* or *0*
        """
        _dir = '{}/emonitor/modules/{}/help'.format(current_app.config.get('PROJECT_ROOT'), self.info['path'])
        if self.helppath != "":
            _dir = '{}{}'.format(current_app.config.get('PROJECT_ROOT'), self.helppath)
        if os.path.exists(_dir):
            return len([fn for fn in os.listdir(_dir) if fn.startswith(area)]) > 0
        else:
            return 0

    def getHelp(self, area="frontend", name=""):  # frontend help template
        """
        Get help text of module for area

        :param optional area: *frontend*, *admin*
        :param optional name: name of sub area
        :return: string of online help
        """
        name = name.replace('help/', '').replace('/', '.')
        if self.helppath == "":
            filename = '{}/emonitor/modules/{}/help/{}.{}.{}.rst'.format(current_app.config.get('PROJECT_ROOT'), self.info['path'], area, current_app.config.get('BABEL_DEFAULT_LOCALE'), name)
        else:
            filename = '{}{}{}.{}.{}.md'.format(current_app.config.get('PROJECT_ROOT'), self.helppath, area, current_app.config.get('BABEL_DEFAULT_LOCALE'), name)

        if os.path.exists(filename):
            with codecs.open(filename, 'r', encoding="utf-8") as helpcontent:
                return helpcontent.read()
        else:
            current_app.logger.info('help: missing help template {}'.format(filename))
        return ""

    def getHelpPaths(self, area="frontend"):
        """
        Get list of all help entries for area

        :param optional area: *frontend*, *area*
        :return: list of filenames
        """
        ret = []
        fn = '{}/emonitor/modules/{}/help'.format(current_app.config.get('PROJECT_ROOT'), self.info['path'])
        if self.helppath != "":
            fn = '{}/{}'.format(current_app.config.get('PROJECT_ROOT'), self.helppath)
        for f in [fn for fn in os.listdir(fn) if fn.startswith(area)]:
            ret.append("/".join(f.split('.')[2:-1]))
        return sorted(ret)

    def getAdminHelp(self, name=""):
        return self.getHelp('admin', name=name)

    def doInit(self):
        pass

    def checkDefinition(self):
        """Check for required parameters of module"""
        return Module.CHECKOK

    def fixDefinition(self, id):
        """Fix default definition"""
        pass

    def getAdminSubNavigation(self):
        """
        Get list of subnavigation entries

        :return: list of entries
        """
        return self.adminsubnavigation

    def updateAdminSubNavigation(self):
        pass

    def getAdminContent(self):
        return "<admin content>"
        
    def getAdminData(self):
        return "<admin data>"

    def getMonitorWidgets(self):
        return self.widgets

    #def getMonitorContent(self):
    #    return "<monitor content>"
        
    def getFrontendContent(self, **params):
        return "<frontend content>"

    def frontendContent(self):
        return 0

    def getWidgets(self):
        return self.widgets

    @staticmethod
    def getPdf(pdfdata):
        """
        Build pdf of module data

        :param pdfdata: content of pdf file
        :return: filename of pdf file
        """
        import random
        images = []

        def link_callback(uri, rel):
            """
            Callback method for links

            :param uri:
            :param rel:
            :return: fixed string for link
            """
            if '/export/' in uri and not rel:  # create tmp-files for export items
                if "/alarms/" in uri and uri.endswith('png'):
                    f, ext = os.path.splitext(uri)
                    from emonitor.modules.alarms.alarm import Alarm
                    fname = '{}{}'.format(current_app.config.get('PATH_TMP'), '{}.png'.format(random.random()))
                    with open(fname, 'wb') as tmpimg:  # write tmp image file
                        tmpimg.write(Alarm.getExportData('.png', style=uri.split('-')[1][:-4], id=f.split('/')[-1].split('-')[0]))
                        images.append(fname)
                    return fname
            return "%s/emonitor/modules%s" % (current_app.config.get('PROJECT_ROOT'), uri)  # make absolute links

        pdf = StringIO()
        try:
            pisa.CreatePDF(StringIO(pdfdata), pdf, link_callback=link_callback)
        except AttributeError:
            logger.debug('AttributeError in pdf creation')

        for image in images:  # remove tmp images
            if os.path.exists(image):
                os.remove(image)

        return pdf.getvalue()


def serialize(root):
    """ serialize dict to xml structure """
    xml = ''
    for key in root.keys():
        if isinstance(root[key], dict):
            xml = '{}<{}>\n{}</{}>\n'.format(xml, key, serialize(root[key]), key)
        elif isinstance(root[key], list):
            xml = '{}<{}>'.format(xml, key)
            for item in root[key]:
                xml = '{}{}'.format(xml, serialize(item))
            xml = '{}</{}>'.format(xml, key)
        else:
            value = root[key]
            xml = '{}<{}>{}</{}>\n'.format(xml, key, value, key)
    return xml


class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def total(self):
        return self.total_count

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def has_first(self):
        return self.page > 1

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or (self.page - left_current - 1 < num < self.page + right_current) or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


def restartService():
    """
    try to restart emonitor app, only if installed as windows service

    :return: 0 if not installed as service or error, 1 if restart done.
    """
    try:
        import win32service
        from service import win32serviceutil, eMonitorService
        win32serviceutil.HandleCommandLine(eMonitorService, argv=['service.py', '--wait', '1', 'restart'])
        return '1'
    except:
        return '0'


def getmarkdown(text):
    try:
        from markdown import markdown
        return Markup(markdown(text))
    except:
        return text


def getreStructuredText(text):
    try:
        from docutils.core import publish_string
        from docutils.writers.html4css1 import Writer as HisWriter

        overrides = {'input_encoding': 'utf-8', 'output_encoding': 'unicode'}
        return Markup(publish_string(source=text, writer=HisWriter(), settings_overrides=overrides))
    except:
        return text


def getJavaSafe(text):
    return re.sub(r"[^0-9a-zA-Z_]+", "", text)
