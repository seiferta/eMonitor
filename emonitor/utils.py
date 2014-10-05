import os
import codecs
from flask import current_app
from math import ceil
from xhtml2pdf import pisa
from StringIO import StringIO
from emonitor import sockethandler


class Classes:
    """ load all modules from module folder in global classes cache """
    classes = {}
    dependencies = {}
    classcache = {}

    def __init__(self):
        pass

    @staticmethod
    def get(classname):
        if classname in Classes.classes:
           # cache classes
            if classname not in Classes.classcache:  # init class once
                Classes.classcache[classname] = Classes.classes[classname]
            return Classes.classcache[classname]
           # classcache end
            #return self.classes[classname]() # deliver new instance
        return None
        
    @staticmethod
    def add(classname, cls):
        Classes.classes[classname] = cls
    
    @staticmethod
    def addDependency(classname, dependon):  # classname->depends on
        if not dependon in Classes.dependencies:
            Classes.dependencies[dependon] = []
        Classes.dependencies[dependon].append(classname)
        
    @staticmethod
    def changes(classname):  # propagate changes in dependent classes
        if classname in Classes.dependencies:
            for cls in Classes.dependencies[classname]:
                if hasattr(Classes.classes[cls], 'dependencyChanged'):
                    Classes.classes[cls]().dependencyChanged(classname)


class Module:

    CHECKOK = 0
    INITNEEDED = 1

    info = {}
    helppath = ""
    
    def __repr__(self):
        return Module.info['name']
    
    def __init__(self, app):
        self.app = app
        self.widgets = []
        self.adminsubnavigation = []
        self.dependency = []  # modulenames with dependency, if module data updated, alert
        self.signalHandler = sockethandler.SocketHandler
    
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
        _dir = '%s/emonitor/modules/%s/help' % (current_app.config.get('PROJECT_ROOT'), self.info['path'])
        if self.helppath != "":
            _dir = '%s%s' % (current_app.config.get('PROJECT_ROOT'), self.helppath)
        if os.path.exists(_dir):
            return len([fn for fn in os.listdir(_dir) if fn.startswith(area)]) > 0
        else:
            return 0

    def getHelp(self, area="frontend", name=""):  # frontend help template
        name = name.replace('help/', '').replace('/', '.')
        if self.helppath == "":
            filename = '%s/emonitor/modules/%s/help/%s.%s.%s.md' % (current_app.config.get('PROJECT_ROOT'), self.info['path'], area, current_app.config.get('BABEL_DEFAULT_LOCALE'), name)
        else:
            filename = '%s%s%s.%s.%s.md' % (current_app.config.get('PROJECT_ROOT'), self.helppath, area, current_app.config.get('BABEL_DEFAULT_LOCALE'), name)

        if os.path.exists(filename):
            with codecs.open(filename, 'r', encoding="utf-8") as helpcontent:
                return helpcontent.read()
        else:
            current_app.logger.info('help: missing help template %s' % filename)
        return ""

    def getHelpPaths(self, area="frontend"):
        ret = []
        fn = '%s/emonitor/modules/%s/help' % (current_app.config.get('PROJECT_ROOT'), self.info['path'])
        if self.helppath != "":
            fn = '%s/%s' % (current_app.config.get('PROJECT_ROOT'), self.helppath)
        for f in [fn for fn in os.listdir(fn) if fn.startswith(area)]:
            ret.append("/".join(f.split('.')[2:-1]))
        return sorted(ret)

    def getAdminHelp(self, name=""):
        return self.getHelp('admin', name=name)

    def doInit(self):
        pass

    def checkDefinition(self):
        return Module.CHECKOK

    def fixDefinition(self, id):
        pass

    def getAdminSubNavigation(self):
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

    @staticmethod
    def getPdf(pdfdata):
        import random
        images = []

        def link_callback(uri, rel):
            if '/export/' in uri and not rel:  # create tmp-files for export items
                if "/alarms/" in uri and uri.endswith('png'):
                    f, ext = os.path.splitext(uri)
                    from emonitor.modules.alarms.alarm import Alarm
                    fname = '%s%s' % (current_app.config.get('PATH_TMP'), '%s.png' % random.random())
                    with open(fname, 'wb') as tmpimg:  # write tmp image file
                        tmpimg.write(Alarm.getExportData('.png', style=uri.split('-')[1][:-4], id=f.split('/')[-1].split('-')[0]))
                        images.append(fname)
                    return fname
            return "%s/emonitor/modules%s" % (current_app.config.get('PROJECT_ROOT'), uri)  # make absolute links

        pdf = StringIO()
        pisa.CreatePDF(StringIO(pdfdata), pdf, link_callback=link_callback)
        for image in images:  # remove tmp images
            if os.path.exists(image):
                os.remove(image)

        return pdf.getvalue()


def serialize(root):
    """ serialize dict to xml structure """
    xml = ''
    for key in root.keys():
        if isinstance(root[key], dict):
            xml = '%s<%s>\n%s</%s>\n' % (xml, key, serialize(root[key]), key)
        elif isinstance(root[key], list):
            xml = '%s<%s>' % (xml, key)
            for item in root[key]:
                xml = '%s%s' % (xml, serialize(item))
            xml = '%s</%s>' % (xml, key)
        else:
            value = root[key]
            xml = '%s<%s>%s</%s>\n' % (xml, key, value, key)
    return xml


def u(s):
    try:
        return s.encode("utf-8")
    except:
        try:
            s = unicode(s)
            return s.decode("latin-1").encode("utf-8")
        except:
            return s


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
