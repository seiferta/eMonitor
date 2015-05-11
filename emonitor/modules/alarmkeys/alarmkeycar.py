from emonitor.extensions import db
from emonitor.modules.cars.car import Car


class AlarmkeyCars(db.Model):
    """AlarmkeyCars class"""

    __tablename__ = 'alarmkeycars'
    __table_args__ = {'extend_existing': True}
    
    kid = db.Column(db.Integer, primary_key=True)
    dept = db.Column(db.String(30), primary_key=True)
    _cars1 = db.Column('cars1', db.String(100), default='')
    _cars2 = db.Column('cars2', db.String(100), default='')
    _material = db.Column('material', db.String(100), default='')

    def _get_cars_proto(self, cartype):  # type 1:cars1, 2:cars2, 3:material
        ret = []
        l = []
        cars = Car.getCars()
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
        self._cars1 = cars1
        self._cars2 = cars2
        self._material = material
        acc = AlarmkeyCars.getAlarmkeyCars(0, dept=dept)
        if acc:
            self.defaultcars1 = acc.cars1
            self.defaultcars2 = acc.cars2
            self.defaultmaterial = acc.materials
        else:
            self.defaultcars1 = []
            self.defaultcars2 = []
            self.defaultmaterial = []

    @staticmethod
    def getAlarmkeyCars(kid=9999, dept=''):
        """
        Get a list of all car objects with given parameters

        :param kid: (optional) id of alarmkey, default = *9999*
        :param dept: (optional) id of department, default = *''*
        :return: list of :py:class:`emonitor.modules.alarmkeys.alarmkeycar.AlarmkeyCars`
        """
        if int(kid) != 9999 and dept != '':
            return AlarmkeyCars.query.filter_by(kid=int(kid), dept=int(dept)).first()
        elif int(kid) == 9999 and dept != '':  # default aao cars for dept
            return AlarmkeyCars.query.filter_by(kid=int(kid), dept=int(dept)).first()
        elif dept != '':
            return AlarmkeyCars.query.filter_by(dept=int(dept)).all()
        else:
            return AlarmkeyCars.query.filter_by(kid=int(kid)).all()
