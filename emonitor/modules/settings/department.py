from sqlalchemy.orm.collections import attribute_mapped_collection
from emonitor.extensions import db, classes
import emonitor.modules.cars.car


class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    color = db.Column(db.String(7))
    orderpos = db.Column(db.Integer)
    defaultcity = db.Column(db.Integer)  # id of default city for this department
    
    cars = db.relationship("Car", collection_class=attribute_mapped_collection('id'), cascade="all, delete-orphan")
    
    def __init__(self, name, color, orderpos, defaultcity=0):
        self.name = name
        self.color = color
        self.orderpos = orderpos
        self.defaultcity = defaultcity
        
    def getCars(self):
        return sorted(self.cars.values(), key=lambda car: car.name)

    def defaultcityname(self):
        return classes.get('city').get_byid(self.defaultcity)
        
    @staticmethod
    def getDefaultDepartment():
        return db.session.query(Department).order_by('orderpost')[0]
        
    @staticmethod
    def getDepartments(id=0):
        if id == 0:
            return db.session.query(Department).order_by('orderpos').all()
        else:
            return db.session.query(Department).filter_by(id=id).first()

    @staticmethod
    def getDeptsDict():
        ret = {}
        for dept in db.session.query(Department).order_by('orderpos'):
            ret[dept.orderpos] = (dept.name, dept.color)
        return ret
        
    @staticmethod
    def count():
        return db.session.query(Department).count()
