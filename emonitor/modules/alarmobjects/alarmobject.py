from sqlalchemy import inspect
from emonitor.modules.streets.street import Street
from emonitor.extensions import db

        
class AlarmObject(db.Model):
    __tablename__ = 'alarmobjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    streetid = db.Column(db.Integer)
    remark = db.Column(db.Text)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    zoom = db.Column(db.Integer)
    alarmplan = db.Column(db.String(5), default='')
    streetno = db.Column(db.String(10), default='')

    def _get_street(self):
        if not inspect(self).session:
            return ''
        return filter(lambda s: s.id == self.streetid, inspect(self).session.query(Street))[0]
    
    street = property(_get_street)

    def __init__(self, name, streetid, remark, lat, lng, zoom, alarmplan, streetno):
        self.name = name
        self.streetid = streetid
        self.remark = remark
        self.lat = lat
        self.lng = lng
        self.zoom = zoom
        self.alarmplan = alarmplan
        self.streetno = streetno
        
    @staticmethod
    def getAlarmObjectsDict():
        ret = {}
        for obj in db.session.query(AlarmObject).order_by('name'):
            ret[obj.id] = obj
        return ret
    
    @staticmethod
    def getAlarmObjects(id=0):
        if id != 0:
            return db.session.query(AlarmObject).filter_by(id=id).first()
        else:
            return db.session.query(AlarmObject).order_by('name').all()
