import imp
import time
import yaml
import ConfigParser
from emonitor.extensions import db
from sqlalchemy.orm.collections import attribute_mapped_collection
from emonitor.modules.settings.settings import Settings


class AlarmType(db.Model):
    """AlarmType class"""
    __tablename__ = 'alarmtypes'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    keywords = db.Column(db.Text, default='')
    interpreter = db.Column(db.String(64))
    sections = db.relationship("AlarmSection", collection_class=attribute_mapped_collection('id'), cascade="all, delete-orphan")
    _translations = db.Column('translations', db.Text)
    _attributes = db.Column('attributes', db.Text)

    def __repr__(self):
        return self.name

    def __init__(self, name, interpreter, keywords='', translations='', attributes=''):
        self.name = name
        self.keywords = keywords
        self.interpreter = interpreter
        self._translations = translations
        self._attributes = attributes

    @staticmethod
    def buildFromConfigFile(cfile):
        """
        create alarmtype from ini file definition

        :param cfile:
        :return: alarmtype
        """
        from emonitor.modules.alarms.alarmsection import AlarmSection
        _cfg = ConfigParser.ConfigParser()
        _cfg.readfp(cfile)

        if not _cfg.has_section('global'):  # global section needed
            return None
        else:
            if 'name' not in _cfg.options('global') or 'class' not in _cfg.options('global'):
                return None

        alarmtype = AlarmType(_cfg.get('global', 'name'), _cfg.get('global', 'class'))
        alarmtype.keywords = _cfg.get('global', 'keywords').replace(u';', u'\r\n')
        t = {}

        for _k, _v in yaml.safe_load(_cfg.get('global', 'translations')).items():
            t[_k.strip()] = _v.strip().encode('utf-8')
        alarmtype.translations = t
        t = {}
        for item in [i for i in _cfg.items('global') if i[0] not in ['keywords', 'name', 'class', 'translations']]:
            t[item[0]] = item[1]
            alarmtype.attributes = t

        for section in _cfg.sections():
            if section != 'global':  # global parameters
                if 'name' not in _cfg.options(section):  # required attribute name missing in section
                    return None

                _params = {}
                for p in [param for param in _cfg.options(section) if param not in ['name', 'method']]:
                    _params[p] = _cfg.get(section, p)

                if 'method' in [k[0] for k in _cfg.items(section)]:
                    _method = _cfg.get(section, 'method')
                else:
                    _method = ""
                alarmtype.sections[_cfg.sections().index(section)] = AlarmSection(alarmtype.id, _cfg.get(section, 'name').decode('utf-8'), section, 1, _method, _cfg.sections().index(section), attributes=yaml.safe_dump(_params, encoding="utf-8"))
        return alarmtype

    def getConfigFile(self):
        """
        build config file from type definition in database

        :return: string in .ini format with [global] and fields as section
        """
        class MyConfigParser(ConfigParser.ConfigParser):
            def getStr(self):
                """Write an .ini-format string representation of the configuration state."""
                ret = []
                if self._defaults:
                    ret.append(u"[DEFAULT]")
                    for (key, value) in self._defaults.items():
                        ret.append(u"{} = {}s".format(key, str(value).replace('\n', '\n\t')))
                    ret.append("\n")

                for _section in self._sections:
                    ret.append(u"\n[{}]".format(_section))
                    for (key, value) in self._sections[_section].items():
                        if key == "__name__":
                            continue
                        if (value is not None) or (self._optcre == self.OPTCRE):
                            key = u" = ".join((key, value.replace(u'\n', u'\n\t')))
                        ret.append(u"{}".format(key))
                return u'\n'.join(ret)

        if self.interpreterclass().configtype == 'generic':  # only regex parsers use config file
            _cfg = MyConfigParser()
            _cfg.add_section('global')
            _cfg.set('global', 'class', self.interpreter)
            _cfg.set('global', 'keywords', self.keywords.replace('\r\n', ';'))
            _cfg.set('global', 'translations', yaml.safe_dump(self.translations, encoding="utf-8"))
            _cfg.set('global', 'name', self.name)
            for k, v in self.attributes.items():
                _cfg.set('global', k, v)

            for section in [s for s in self.getSections() if s.active]:
                _cfg.add_section(section.key)
                _cfg.set(section.key, 'name', section.name)
                if section.method:
                    _cfg.set(section.key, 'method', section.method)

                for _k, _v in section.attributes.items():
                    _cfg.set(section.key, _k, _v)
            return _cfg.getStr()
        else:
            return ""

    @property
    def translations(self):
        return yaml.load(self._translations) or {}

    @translations.setter
    def translations(self, values):
        self._translations = yaml.safe_dump(values, encoding='utf-8')

    @property
    def attributes(self):
        """
        getter for attributes

        :return: dict with type attributes
        """
        return yaml.load(self._attributes) or {}

    @attributes.setter
    def attributes(self, values):
        """
        setter for type attributes
        :param values: digt with key-value pairs
        """
        self._attributes = yaml.safe_dump(values, encoding='utf-8')

    def interpreterclass(self):
        """
        Get type interpreter class from directory *emonitor/modules/alarms/inc/*

        :return: interpreterlass as instance :py:class:`emonitor.modules.alarms.alarmutils.AlarmFaxChecker`
        """
        if self.interpreter:
            cls = imp.load_source('emonitor.modules.alarms.inc', 'emonitor/modules/alarms/inc/%s' % self.interpreter)
            return getattr(cls, cls.__all__[0])()
        return None

    def interpreterStrings(self):
        """
        Get list of needed string for interpreter class

        :return: list of strings
        """
        if self.interpreterclass():
            return sorted(self.interpreterclass().getDefaultConfig()['translations'])
        return []

    def translation(self, name):
        if name in self.translations:
            return self.translations[name]
        return ""
        
    def getSections(self):
        """
        Get sorted list of possible sections of :py:class:`emonitor.modules.alarms.alarmtype.AlarmType`

        :return: list of :py:class:`emonitor.modules.alarms.alarmsection.AlarmSection`
        """
        return sorted(self.sections.values())

    @staticmethod
    def getVariables():
        return Settings.get('alarms.evalfields').split('\r\n')

    @staticmethod
    def getAlarmTypes(id=0):
        """
        Get list of alarm type objects filtered by parameter

        :param optional id: id of alarm type or 0 for all types
        :return: list of single object :py:class:`emonitor.modules.alarms.alarmtype.AlarmType`
        """
        if id != 0:
            return AlarmType.query.filter_by(id=id).first()
        else:
            return AlarmType.query.order_by('id').all()

    @staticmethod
    def getAlarmTypeByClassname(name):
        """
        Get list of all alarm types by given class name

        :param name: name of interpreter class
        :return: list of :py:class:`emonitor.modules.alarms.alarmtype.AlarmType`
        """
        return AlarmType.query.filter_by(interpreter=name).all() or []

    @staticmethod
    def handleEvent(eventname, **kwargs):
        """
        Eventhandler for alarm type class: do type detection

        :param eventname:
        :param kwargs:
        :return:
        """
        stime = time.time()
        
        if 'text' in kwargs.keys():
            text = kwargs['text']
            atype = None
            for alarmtype in AlarmType.getAlarmTypes():
                for kw in alarmtype.keywords.split('\n'):
                    if kw in text:
                        atype = alarmtype
                        break
            
            kwargs['type'] = 0
            if atype:
                kwargs['type'] = atype.id

        if 'time' not in kwargs.keys():
            kwargs['time'] = []
        kwargs['time'].append('alarmtype: alarmtype detection done in %s sec.' % (time.time() - stime))
        
        return kwargs
