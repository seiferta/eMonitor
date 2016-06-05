from sqlalchemy.orm import relationship
from emonitor.extensions import db
from .alarmtype import AlarmType
import yaml

    
class AlarmSection(db.Model):
    """
    AlarmSection class for sections of alarm type :py:class:`emonitor.modules.alarms.alarmtype.AlarmType`
    """
    __tablename__ = 'alarmsections'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    tid = db.Column(db.Integer, db.ForeignKey('alarmtypes.id'))
    name = db.Column(db.String(32), default="")
    key = db.Column(db.String(32), default="")
    active = db.Column(db.Integer, default=0)
    method = db.Column(db.Text, default="")
    orderpos = db.Column(db.Integer, default=0)
    _attributes = db.Column('attributes', db.Text)

    alarmtype = relationship(AlarmType.__name__, backref="tid", lazy='joined')
    
    def __init__(self, tid, name, key, active, method, orderpos, attributes=''):
        self.tid = tid
        self.name = name
        self.key = key
        self.active = active
        self.method = method
        self.orderpos = orderpos
        self._attributes = attributes

    def __repr__(self):
        return '{}: {} {}'.format(self.orderpos, self.name.encode('utf-8'), self.key.encode('utf-8'))

    def __cmp__(self, other):
        if hasattr(other, 'orderpos'):
            return self.orderpos.__cmp__(other.orderpos)

    @property
    def attributes(self):
        return yaml.load(self._attributes) or {}

    @attributes.setter
    def attributes(self, values):
        self._attributes = yaml.safe_dump(values, encoding='utf-8')

    def getSectionMethod(self):
        return self.method.split(';')[0]
        
    def getSectionMethodParams(self):
        if len(self.method.split(';')) > 1:
            return ','.join(self.method.split(';')[1:])
        return ''

    def getSectionMethodConfig(self, attribute=''):
        """
        Get attributes from yaml object
        :param attribute: attribute name of method yaml dict
        :return: value of given attribute or yaml dict
        """
        val = yaml.load(self.method)
        if attribute in val.keys():
            return val[attribute]
        return val

    @staticmethod
    def getSections(id=0, tid=0):
        """
        Get list of sections of current alarmtype

        :param optional id: section id, 0 for all sections
        :param optional tid: type id, 0 for all types
        :return: list of :py:class:`emonitor.modules.alarms.alarmsection.AlarmSection`
        """
        if id != 0:
            return AlarmSection.query.filter_by(id=id).first()
        elif tid != 0:
            return AlarmSection.query.filter_by(tid=int(tid)).order_by('orderpos').all()
        else:
            return AlarmSection.query.order_by('orderpos').all()
