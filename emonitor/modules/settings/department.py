import os
import yaml
from sqlalchemy.orm.collections import attribute_mapped_collection
from emonitor.extensions import db


class Department(db.Model):
    """Department class"""
    __tablename__ = 'departments'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    shortname = db.Column(db.String(10))
    color = db.Column(db.String(7))
    orderpos = db.Column(db.Integer)
    defaultcity = db.Column(db.Integer)  # id of default city for this department
    _attributes = db.Column('attributes', db.Text)

    def _get_city(self):
        from emonitor.modules.streets.city import City
        return City.getCities(self.defaultcity)

    city = property(_get_city)
    cars = db.relationship("Car", collection_class=attribute_mapped_collection('id'), cascade="all, delete-orphan")

    def __init__(self, name, shortname, color, orderpos, defaultcity=0, attributes={}):
        self.name = name
        self.shortname = shortname
        self.color = color
        self.orderpos = orderpos
        self.defaultcity = defaultcity
        self._attributes = yaml.safe_dump(attributes, encoding='utf-8')

    def __getattr__(self, name, default=''):
        if name in self.attributes:
            return self.attributes[name]
        else:
            return default

    @property
    def attributes(self):
        return yaml.load(self._attributes)

    @attributes.setter
    def attributes(self, attrs):
        self._attributes = yaml.safe_dump(attrs, encoding='utf-8')

    def set(self, name, value):
        attrs = self.attributes
        attrs[name] = value
        self.attributes = attrs

    def getCars(self):
        return sorted(self.cars.values(), key=lambda car: car.name)

    def getLogoStream(self):
        """
        Deliver logo file as stream, base 64 encoded

        :return: base 64 stream or empty string
        """
        from emonitor import app
        if self.attributes['logo'] != '' and os.path.exists('{}{}'.format(app.config.get('PATH_DATA'), self.attributes['logo'])):
            return open('{}{}'.format(app.config.get('PATH_DATA'), self.attributes['logo']), 'rb').read().encode("base64")
        else:
            return open('{}/emonitor/frontend/web/img/empty.png'.format(app.config.get('PROJECT_ROOT')), 'rb').read().encode("base64")

    @staticmethod
    def getDefaultDepartment():
        """Get default department :py:class:`emonitor.modules.settings.department.Department`"""
        return Department.query.order_by('orderpos').first()

    @staticmethod
    def getDepartments(id=0):
        """
        Get department list filtered by criteria

        :param optional id: id of department, *0* for all
        :return: list of :py:class:`emonitor.modules.settings.department.Department`
        """
        if id == 0:
            return Department.query.order_by('orderpos').all()
        else:
            return Department.query.filter_by(id=id).first()

    @staticmethod
    def getDeptsDict():
        """
        Get departements as dict

        :return: dict of :py:class:`emonitor.modules.settings.department.Department`
        """
        ret = {}
        for dept in Department.query.order_by('orderpos'):
            ret[dept.orderpos] = (dept.name, dept.color)
        return ret
