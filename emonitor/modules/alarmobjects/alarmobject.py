import yaml
from emonitor.extensions import classes
from emonitor.modules.streets.street import Street
from emonitor.modules.alarmobjects.alarmobjecttype import AlarmObjectType
from emonitor.modules.alarmobjects.alarmobjectfile import AlarmObjectFile
from sqlalchemy.orm.collections import attribute_mapped_collection
from emonitor.extensions import db


class AlarmObject(db.Model):
    __tablename__ = 'alarmobjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    _streetid = db.Column('streetid', db.ForeignKey('streets.id'))
    _objecttype = db.Column('typeid', db.ForeignKey('alarmobjecttypes.id'))
    _attributes = db.Column('attributes', db.Text)
    remark = db.Column(db.Text)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    zoom = db.Column(db.Integer)
    alarmplan = db.Column(db.String(5), default='')
    streetno = db.Column(db.String(10), default='')
    bma = db.Column(db.String(10), default='')
    active = db.Column(db.Integer)
    street = db.relationship(Street, collection_class=attribute_mapped_collection('id'), lazy='subquery')
    objecttype = db.relationship(AlarmObjectType, collection_class=attribute_mapped_collection('id'), lazy='subquery')
    files = db.relationship(AlarmObjectFile, collection_class=attribute_mapped_collection('id'), cascade="all, delete-orphan", lazy='subquery')

    def __init__(self, name, streetid, remark, lat, lng, zoom, alarmplan, streetno, bma, active, objecttype):
        self.name = name
        self._streetid = streetid
        self.remark = remark
        self.lat = lat
        self.lng = lng
        self.zoom = zoom
        self.alarmplan = alarmplan
        self.streetno = streetno
        self.bma = bma
        self.active = active
        self._objecttype = objecttype

    @property
    def serialize(self):
        return dict(id=self.id, name=self.name, lat=self.lat, lng=self.lng, zoom=self.zoom, alarmplan=self.alarmplan, street=self.street.serialize, streetno=self.streetno)

    def get(self, attribute):
        try:
            values = yaml.load(self._attributes)
            return values[attribute]
        except:
            return ""

    def set(self, attribute, val):
        try:
            values = yaml.load(self._attributes)
        except:
            values = {}
        values[attribute] = val
        self._attributes = yaml.safe_dump(values, encoding='utf-8')

    def getCars1(self):
        return [c for c in classes.get('car').getCars() if str(c.id) in (self.get('cars1') or [])]

    def getCars2(self):
        return [c for c in classes.get('car').getCars() if str(c.id) in (self.get('cars2') or [])]

    def getMaterial(self):
        return [c for c in classes.get('car').getCars() if str(c.id) in (self.get('material') or [])]

    def hasOwnAAO(self):
        return len(self.get('cars1') + self.get('cars2') + self.get('material')) > 0

    @staticmethod
    def getAlarmObjectsDict():
        ret = {}
        for obj in db.session.query(AlarmObject).order_by('name'):
            ret[obj.id] = obj
        return ret
    
    @staticmethod
    def getAlarmObjects(id=0, active=1):
        if id != 0:
            return db.session.query(AlarmObject).filter_by(id=id).first()
        else:
            if active == 1:  # only active objects
                return db.session.query(AlarmObject).filter_by(active=1).order_by('name').all()
            else:  # deliver all objects
                return db.session.query(AlarmObject).order_by('name').all()
