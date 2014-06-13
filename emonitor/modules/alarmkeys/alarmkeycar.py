from sqlalchemy import inspect
from emonitor.extensions import db, classes


class AlarmkeyCars(db.Model):
    __tablename__ = 'alarmkeycars'
    
    kid = db.Column(db.Integer, primary_key=True)
    dept = db.Column(db.String(30), primary_key=True)
    _cars1 = db.Column('cars1', db.String(100), default='')
    _cars2 = db.Column('cars2', db.String(100), default='')
    _material = db.Column('material', db.String(100), default='')

    def _get_cars_proto(self, cartype):  # type 1:cars1, 2:cars2, 3:material
        ret = []
        l = []
        if not inspect(self).session:
            return ret
        cars = inspect(self).session.query(classes.get('car'))
        try:
            if cartype == 1:
                l = [int(i) for i in self._cars1.split(';') if i != '']
            elif cartype == 2:
                l = [int(i) for i in self._cars2.split(';') if i != '']
            elif cartype == 3:
                l = [int(i) for i in self._material.split(';') if i != '']
        except:
            l = []

        for c_id in l:
            c = filter(lambda c: c.id == c_id, cars)
            if len(c) == 1:
                ret.append(c[0])
        return ret
    
    # cars1
    def _get_cars1(self):
        return self._get_cars_proto(1)

    def _get_cars1id(self):
        return [int(i) for i in self._cars1.split(';') if i != '']

    # cars2
    def _get_cars2(self):
        return self._get_cars_proto(2)

    def _get_cars2id(self):
        return [int(i) for i in self._cars2.split(';') if i != '']

    # material
    def _get_material(self):
        return self._get_cars_proto(3)

    def _get_materialid(self):
        return [int(i) for i in self.material.split(';') if i != '']

    car1id = property(_get_cars1id)
    cars1 = property(_get_cars1)
    car2id = property(_get_cars2id)
    cars2 = property(_get_cars2)
    materialid = property(_get_materialid)
    materials = property(_get_material)

    def __init__(self, kid, dept, cars1, cars2, material):
        self.kid = kid
        self.dept = dept
        self._cars1 = cars1
        self._cars2 = cars2
        self._material = material
        
        acc = AlarmkeyCars.getAlarmkeyCars(kid=0, dept=dept)
        if acc:
            self.defaultcars1 = acc.cars1
            self.defaultcars2 = acc.cars2
            self.defaultmaterial = acc.materials
        else:
            self.defaultcars1 = []
            self.defaultcars2 = []
            self.defaultmaterial = []
            
    """
    def getCar1ids(self):
        return [i.id for i in self.cars1 if i != '']
        
    def getCar2ids(self):
        return [i.id for i in self.cars2 if i != '']
        
    def getMaterialids(self):
        return [i.id for i in self.material if i != '']
        
    def getCar1cars(self):
        cars = classes.get('car').getCarsDict()
        ret = []
        for c in [i for i in self.cars1.split(';') if i != '']:
            ret.append(cars[c])
        return ret
    """
    def defaultUsed(self, cartype='cars1'):
        if cartype == 'cars1':
            return self.cars1 == ''
        elif cartype == 'cars2':
            return self.cars2 == ''
        else:
            return self.material == ''
        
    @staticmethod
    def getAlarmkeyCars(kid=0, dept=''):
        if kid != 0 and dept != '':
            return db.session.query(classes.get('alarmkeycar')).filter_by(kid=int(kid), dept=int(dept)).first()
        elif dept != '':
            return db.session.query(classes.get('alarmkeycar')).filter_by(dept=int(dept)).all()
        else:
            return db.session.query(classes.get('alarmkeycar')).filter_by(kid=int(kid)).all()
