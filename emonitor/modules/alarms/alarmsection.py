from sqlalchemy.orm import relationship
from emonitor.extensions import db
from .alarmtype import AlarmType

    
class AlarmSection(db.Model):
    __tablename__ = 'alarmsections'
    
    id = db.Column(db.Integer, primary_key=True)
    tid = db.Column(db.Integer, db.ForeignKey('alarmtypes.id'))
    name = db.Column(db.String(32), default="")
    key = db.Column(db.String(32), default="")
    active = db.Column(db.Integer, default=0)
    method = db.Column(db.Text, default="")
    orderpos = db.Column(db.Integer, default=0)

    alarmtype = relationship(AlarmType.__name__, backref="tid", lazy='joined')
    
    def __init__(self, tid, name, key, active, method, orderpos):
        self.tid = tid
        self.name = name
        self.key = key
        self.active = active
        self.method = method
        self.orderpos = orderpos

    def __repr__(self):
        return '{}: {} {}'.format(self.orderpos, self.name, self.key)

    def __cmp__(self, other):
        if hasattr(other, 'orderpos'):
            return self.orderpos.__cmp__(other.orderpos)

    def getSectionMethod(self):
        return self.method.split(';')[0]
        
    def getSectionMethodParams(self):
        if len(self.method.split(';')) > 1:
            return ','.join(self.method.split(';')[1:])
        return ''

    @staticmethod
    def getSections(id=0, tid=0):
        if id != 0:
            return db.session.query(AlarmSection).filter_by(id=id).first()
        elif tid != 0:
            return db.session.query(AlarmSection).filter_by(tid=int(tid)).order_by('orderpos').all()
        else:
            return db.session.query(AlarmSection).order_by('orderpos').all()
