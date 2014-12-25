import imp
import time
import yaml
from emonitor.extensions import db, classes
from sqlalchemy.orm.collections import attribute_mapped_collection


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

    def __repr__(self):
        return self.name

    def __init__(self, name, interpreter, keywords='', translations=''):
        self.name = name
        self.keywords = keywords
        self.interpreter = interpreter
        self._translations = translations

    @property
    def translations(self):
        return yaml.load(self._translations) or {}

    @translations.setter
    def translations(self, values):
        self._translations = yaml.safe_dump(values, encoding='utf-8')

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
        Get list of nedded string for interpreter class

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
        return classes.get('settings').get('alarms.evalfields').split('\r\n')

    @staticmethod
    def getAlarmTypes(id=0):
        """
        Get list of alarm type objects filtered by parameter

        :param optional id: id of alarm type or 0 for all types
        :return: list of single object :py:class:`emonitor.modules.alarms.alarmtype.AlarmType`
        """
        if id != 0:
            return db.session.query(AlarmType).filter_by(id=id).first()
        else:
            return db.session.query(AlarmType).order_by('id').all()

    @staticmethod
    def getAlarmTypeByClassname(name):
        """
        Get list of all alarm types by given class name

        :param name: name of interpreter class
        :return: list of :py:class:`emonitor.modules.alarms.alarmtype.AlarmType`
        """
        return db.session.query(AlarmType).filter_by(interpreter=name).all() or []

    @staticmethod
    def handleEvent(eventname, *kwargs):
        """
        Eventhandler for alarm type class: do type detection

        :param eventname:
        :param kwargs:
        :return:
        """
        stime = time.time()
        
        if 'text' in kwargs[0]:
            text = kwargs[0]['text']
            atype = None
            for alarmtype in classes.get('alarmtype').getAlarmTypes():
                for kw in alarmtype.keywords.split('\n'):
                    if kw in text:
                        atype = alarmtype
                        break
            
            kwargs[0]['type'] = 0
            if atype:
                kwargs[0]['type'] = atype.id

        if 'time' not in kwargs[0]:
            kwargs[0]['time'] = []
        kwargs[0]['time'].append('alarmtype: alarmtype detection done in %s sec.' % (time.time() - stime))
        
        return kwargs
