import yaml
from emonitor.modules.streets.street import Street
from emonitor.modules.alarmobjects.alarmobjecttype import AlarmObjectType
from emonitor.modules.alarmobjects.alarmobjectfile import AlarmObjectFile
from emonitor.modules.cars.car import Car
from sqlalchemy.orm.collections import attribute_mapped_collection
from emonitor.extensions import db


class AlarmObject(db.Model):
    """AlarmObject class"""
    __tablename__ = 'alarmobjects'
    __table_args__ = {'extend_existing': True}
    
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

    def get(self, attribute, default=""):
        """
        Getter for attribute names

        :param attribute: name of attribute as string
        :param optional default: default value
        :return: value of attribute
        """
        try:
            values = yaml.load(self._attributes)
            return values[attribute]
        except:
            return default

    def set(self, attribute, val):
        """
        Setter for attributes

        :param attribute: attribute name as string
        :param val: value as string
        """
        try:
            values = yaml.load(self._attributes)
        except:
            values = {}
        values[attribute] = val
        self._attributes = yaml.safe_dump(values, encoding='utf-8')

    def get_cars_proto(self, ctype):
        """
        Prototype of car, material getter

        :param ctype: 1:cars1, 2:cars2, 3:material
        :return: list of :py:class:`emonitor.modules.cars.car.Car`
        """
        _t = {1: 'cars1', 2: 'cars2', 3: 'material'}
        ret = []
        cars = Car.getCars()
        for _c in [int(c) for c in self.get(_t[ctype]) if c != '']:
            try:
                ret.append(filter(lambda c: c.id == _c, cars)[0])
            except IndexError:
                pass
        return ret

    def getCars1(self):
        return self.get_cars_proto(1)

    def getCars2(self):
        return self.get_cars_proto(2)

    def getMaterial(self):
        return self.get_cars_proto(3)

    def hasOwnAAO(self):
        return len(self.get('cars1') + self.get('cars2') + self.get('material')) > 0

    @staticmethod
    def getAlarmObjectsDict():
        return dict((_o.id, _o) for _o in AlarmObject.query.order_by('name'))

    @staticmethod
    def getAlarmObjects(id=0, active=1):
        """
        Get list of alarmobjects with given params

        :param id: id of alarmobject or *0* for all objects
        :param active: *1* for active objects or *0* for all objects
        :return: list of :py:class:`emonitor.modules.alarmobjects.alarmobject.AlarmObject`
        """
        if id != 0:
            return AlarmObject.query.filter_by(id=id).first()
        else:
            if active == 1:  # only active objects
                return AlarmObject.query.filter_by(active=1).order_by('name').all()
            else:  # deliver all objects
                return AlarmObject.query.order_by('name').all()
