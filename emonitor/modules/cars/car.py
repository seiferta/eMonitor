from sqlalchemy.orm.collections import attribute_mapped_collection
from emonitor.extensions import db, classes


class Car(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    fmsid = db.Column(db.String(8))
    active = db.Column(db.Integer)
    type = db.Column(db.Text)
    _dept = db.Column('dept', db.ForeignKey('departments.id'))
    
    dept = db.relationship("Department", collection_class=attribute_mapped_collection('id'))
    
    def __init__(self, name, description, fmsid, active, type, dept):
        self.name = name
        self.description = description
        self.fmsid = fmsid
        self.active = active
        self.type = type
        self._dept = dept
        
    def getColor(self):
        for t in classes.get("settings").getCarTypes():
            if t[0] == self.type:
                return t[1]
        return "#ffffff"
        
    def __str__(self):
        return self.name

    @staticmethod
    def getCars(id=0, deptid=0, params=[]):
        if id != 0:
            return db.session.query(Car).filter_by(id=int(id)).first()
        elif int(deptid) != 0:
            return db.session.query(Car).filter_by(_dept=int(deptid)).order_by('name').all()
        else:
            if 'onlyactive' in params:
                return db.session.query(Car).filter_by(active=1).order_by('dept', 'name').all()
            else:
                return db.session.query(Car).order_by('dept', 'name').all()

    @staticmethod
    def getCarsDict():
        ret = {}
        for car in db.session.query(Car):
            ret[car.id] = car
        return ret
