from sqlalchemy.orm.collections import attribute_mapped_collection
from emonitor.extensions import db, classes
import emonitor.modules.cars.car


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
    
    cars = db.relationship("Car", collection_class=attribute_mapped_collection('id'), cascade="all, delete-orphan")
    
    def __init__(self, name, shortname, color, orderpos, defaultcity=0):
        self.name = name
        self.shortname = shortname
        self.color = color
        self.orderpos = orderpos
        self.defaultcity = defaultcity
        
    def getCars(self):
        return sorted(self.cars.values(), key=lambda car: car.name)

    def defaultcityname(self):
        return classes.get('city').get_byid(self.defaultcity)
        
    @staticmethod
    def getDefaultDepartment():
        """Get default department :py:class:`emonitor.modules.settings.department.Department`"""
        return db.session.query(Department).order_by('orderpos').first()
        
    @staticmethod
    def getDepartments(id=0):
        """
        Get department list filtered by criteria

        :param optional id: id of department, *0* for all
        :return: list of :py:class:`emonitor.modules.settings.department.Department`
        """
        if id == 0:
            try:
                return db.session.query(Department).order_by('orderpos').all()
            except:
                return []
        else:
            return db.session.query(Department).filter_by(id=id).first()

    @staticmethod
    def getDeptsDict():
        """
        Get departements as dict

        :return: dict of :py:class:`emonitor.modules.settings.department.Department`
        """
        ret = {}
        for dept in db.session.query(Department).order_by('orderpos'):
            ret[dept.orderpos] = (dept.name, dept.color)
        return ret
        
    @staticmethod
    def count():
        """
        Get number of departments as integer

        :return: number of departments
        """
        return db.session.query(Department).count()
