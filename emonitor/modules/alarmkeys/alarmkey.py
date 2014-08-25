from emonitor.extensions import db, classes


class Alarmkey(db.Model):
    __tablename__ = 'alarmkeys'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(40), default='')
    key = db.Column(db.String(40), default='')
    key_internal = db.Column(db.String(40), default='')
    remark = db.Column(db.Text)

    def __init__(self, category, key, key_internal, remark):
        self.category = category
        self.key = key
        self.key_internal = key_internal
        self.remark = remark

    def _getCars(self, cartype, department):
        alarmcars = db.session.query(classes.get('alarmkeycar')).filter_by(kid=self.id or 0, dept=department).first()

        if not alarmcars:
            # try default
            alarmcars = db.session.query(classes.get('alarmkeycar')).filter_by(kid=0, dept=department).first()

        if alarmcars:
            if cartype == 1:
                return alarmcars.cars1
            elif cartype == 2:
                return alarmcars.cars2
            elif cartype == 3:
                return alarmcars.materials
        else:
            return []

    def setCars(self, department, **kwargs):
        alarmcars = db.session.query(classes.get('alarmkeycar')).filter_by(kid=self.id, dept=department).first()
        if not alarmcars:
            alarmcars = classes.get('alarmkeycar')(self.id, department, '', '', '')
            db.session.add(alarmcars)
        if "cars1" in kwargs.keys():
            alarmcars._cars1 = kwargs['cars1']
        if "cars2" in kwargs.keys():
            alarmcars._cars2 = kwargs['cars2']
        if "material" in kwargs.keys():
            alarmcars._materials = kwargs['materials']

    def getCars1(self, department):
        return self._getCars(1, department)

    def getCars2(self, department):
        return self._getCars(2, department)

    def getMaterial(self, department):
        return self._getCars(3, department)

    def hasDefinition(self, department):
        return db.session.query(classes.get('alarmkeycar')).filter_by(kid=self.id or 0, dept=department).first() is None

    @staticmethod
    def getAlarmkeys(id=''):
        if id not in ['', 'None']:
            return db.session.query(classes.get('alarmkey')).filter_by(id=int(id)).first()
        else:
            return db.session.query(classes.get('alarmkey')).order_by('category').all()

    @staticmethod
    def getAlarmkeysByName(name):
        return db.session.query(classes.get('alarmkey')).filter(classes.get('alarmkey').key.like('%' + name + '%')).all()

    @staticmethod
    def getAlarmkeysByCategory(category):
        return db.session.query(classes.get('alarmkey')).filter_by(category=category).all()

    @staticmethod
    def getAlarmkeysDict():
        ret = {}
        for k in db.session.query(classes.get('alarmkey')):
            ret[k.id] = k
        return ret

    @staticmethod
    def getDefault(department):
        return db.session.query(classes.get('alarmkeycar')).filter_by(kid=0, dept=department).first() or classes.get(
            'alarmkeycar')(0, department, '', '', '')
