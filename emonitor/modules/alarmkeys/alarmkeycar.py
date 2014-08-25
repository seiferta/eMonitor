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

    def _set_cars1(self, cars):
        self._cars1 = cars

    def _get_cars1id(self):
        return [int(i) for i in self._cars1.split(';') if i != '']

    # cars2
    def _get_cars2(self):
        return self._get_cars_proto(2)

    def _set_cars2(self, cars):
        self._cars2 = cars

    def _get_cars2id(self):
        return [int(i) for i in self._cars2.split(';') if i != '']

    # material
    def _get_material(self):
        return self._get_cars_proto(3)

    def _set_material(self, material):
        self._material = material

    def _get_materialid(self):
        return [int(i) for i in self.material.split(';') if i != '']

    car1id = property(_get_cars1id)
    cars1 = property(_get_cars1, _set_cars1)
    car2id = property(_get_cars2id)
    cars2 = property(_get_cars2, _set_cars2)
    materialid = property(_get_materialid)
    materials = property(_get_material, _set_material)

    def __init__(self, kid, dept, cars1, cars2, material):
        self.kid = kid
        self.dept = dept
        self.cars1 = cars1
        self.cars2 = cars2
        self.material = material
        acc = AlarmkeyCars.getAlarmkeyCars(0, dept=dept)
        if acc:
            self.defaultcars1 = acc[0].cars1
            self.defaultcars2 = acc[0].cars2
            self.defaultmaterial = acc[0].materials
        else:
            self.defaultcars1 = []
            self.defaultcars2 = []
            self.defaultmaterial = []

    def defaultUsed(self, cartype='cars1'):
        if cartype == 'cars1':
            return self.cars1 == ''
        elif cartype == 'cars2':
            return self.cars2 == ''
        else:
            return self.material == ''

    @staticmethod
    def getAlarmkeyCars(kid=0, dept=''):
        if int(kid) != 0 and dept != '':
            return db.session.query(classes.get('alarmkeycar')).filter_by(kid=int(kid), dept=int(dept)).first()
        elif dept != '':
            return db.session.query(classes.get('alarmkeycar')).filter_by(dept=int(dept)).all()
        else:
            return db.session.query(classes.get('alarmkeycar')).filter_by(kid=int(kid)).all()
