import imp
import time
import yaml
from emonitor.extensions import db, classes
from sqlalchemy.orm.collections import attribute_mapped_collection


class AlarmType(db.Model):
    __tablename__ = 'alarmtypes'
    
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
        cls = imp.load_source('emonitor.modules.alarms.inc', 'emonitor/modules/alarms/inc/%s' % self.interpreter)
        return getattr(cls, cls.__all__[0])()

    def translation(self, name):
        if name in self.translations:
            return self.translations[name]
        return ""
        
    def getSections(self):
        return self.sections.values()

    @staticmethod
    def getVariables():
        return classes.get('settings').get('alarms.evalfields').split('\r\n')

    @staticmethod
    def getAlarmTypes(id=0):
        if id != 0:
            return db.session.query(AlarmType).filter_by(id=id).first()
        else:
            return db.session.query(AlarmType).order_by('id').all()

    @staticmethod
    def handleEvent(eventname, *kwargs):
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

        if not 'time' in kwargs[0]:
            kwargs[0]['time'] = []
        kwargs[0]['time'].append('alarmtype: alarmtype detection done in %s sec.' % (time.time() - stime))
        
        return kwargs
