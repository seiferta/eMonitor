from sqlalchemy.orm.collections import attribute_mapped_collection
from emonitor.extensions import db
from emonitor.modules.alarmkeys.alarmkeycar import AlarmkeyCars
from emonitor.modules.alarmkeys.alarmkeyset import AlarmkeySet


class Alarmkey(db.Model):
    """Alarmkey class"""
    __tablename__ = 'alarmkeys'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(40), default='')
    key = db.Column(db.String(40), default='')
    key_internal = db.Column(db.String(40), default='')
    _keyset = db.Column('keyset', db.ForeignKey('alarmkeysets.id'))
    keyset = db.relationship("AlarmkeySet", collection_class=attribute_mapped_collection('id'))
    keysetitem = db.Column(db.INTEGER, default=0)
    remark = db.Column(db.Text)

    def __init__(self, category, key, key_internal, remark, keyset=None, keysetitem=None):
        self.category = category
        self.key = key
        self.key_internal = key_internal
        self.remark = remark
        self._keyset = keyset
        self.keysetitem = keysetitem

    def _getCars(self, cartype, department):
        """
        Prototype method for car or material lists

        :param cartype: 1|2|3: cars1, cars2, material as integer
        :param department: id of department as integer
        :return: list of cars, material
        """
        alarmcars = AlarmkeyCars.getAlarmkeyCars(kid=self.id or 9999, dept=department)

        if not alarmcars:
            # try default
            alarmcars = AlarmkeyCars.getAlarmkeyCars(kid=9999, dept=department)

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
        """
        Set carlist of department

        :param department: id of department as integer
        :param kwargs:
            - *cars1*: list of :py:class:`emonitor.modules.cars.car.Car` objects for cars1
            - *cars2*: list of :py:class:`emonitor.modules.cars.car.Car` objects for cars2
            - *material*: list of :py:class:`emonitor.modules.cars.car.Car` objects for material
        """
        alarmcars = AlarmkeyCars.getAlarmkeyCars(kid=self.id, dept=department)
        if not alarmcars:
            alarmcars = AlarmkeyCars(self.id, department, '', '', '')
            db.session.add(alarmcars)
        if "cars1" in kwargs.keys():
            alarmcars._cars1 = kwargs['cars1']
        if "cars2" in kwargs.keys():
            alarmcars._cars2 = kwargs['cars2']
        if "material" in kwargs.keys():
            alarmcars._material = kwargs['material']

    def getCars1(self, department):
        """
        Get list of Car objects for cars1 of current alarmkey definition of given department

        :param department: id of department as integer
        :return: list of :py:class:`emonitor.modules.cars.car.Car` objects
        """
        return self._getCars(1, department)

    def getCars2(self, department):
        """
        Get list of Car objects for cars2 of current alarmkey definition of given department

        :param department: id of department as integer
        :return: list of :py:class:`emonitor.modules.cars.car.Car` objects
        """
        return self._getCars(2, department)

    def getMaterial(self, department):
        """
        Get list of Car objects for material of current alarmkey definition of given department

        :param department: id of department as integer
        :return: list of :py:class:`emonitor.modules.cars.car.Car` objects
        """
        return self._getCars(3, department)

    def hasDefinition(self, department):
        """
        Get definition for current alarmkey of given department

        :param department: id of department
        :return: :py:class:`emonitor.modules.alarmkeys.alarmkey.Alarmkey` or *None*
        """
        return AlarmkeyCars.getAlarmkeyCars(kid=self.id or 9999, dept=department) is None

    @staticmethod
    def getAlarmkeys(id='', keysetid=None):
        """
        Get all alarmkey definitions or single definition with given 'id'

        :param id: id of alarmkey
        :param keysetid: id of :py:class:`emonitor.modules.alarmkeys.AlarmkeySet` oder *None*
        :return: list of defintions or single definition
        """
        if id not in ['', 'None']:
            return Alarmkey.query.filter_by(id=id).first()
        elif keysetid:
            if int(keysetid) == 0:  # deliver all un-matched items
                return Alarmkey.query.filter_by(_keyset=None).order_by('category').all()
            return Alarmkey.query.filter_by(_keyset=keysetid).order_by('category').all()
        else:
            keyset = AlarmkeySet.getCurrentKeySet()
            if keyset is None:
                return Alarmkey.query.order_by('category').all()
            else:
                return Alarmkey.query.filter_by(_keyset=keyset.id).order_by('category').all()

    @staticmethod
    def getOrphanKeys():
        """
        Get list of all orphan alarmkeys

        :return: list of orphan alarmkeys
        """
        return Alarmkey.query.filter_by(keyset=None).all()

    @staticmethod
    def getAlarmkeysByName(name):
        """
        Get Alarmkey object with given name

        :param name: name as string (like)
        :return: :py:class:`emonitor.modules.alarmkeys.alarmkey.Alarmkey` object
        """
        return Alarmkey.query.filter(Alarmkey.key.like('%' + name + '%')).all()

    @staticmethod
    def getAlarmkeysByCategory(category):
        """
        Get all alarmkey definitions of given category

        :param category: category as string
        :return: :py:class:`emonitor.modules.alarmkeys.alarmkey.Alarmkey` object list
        """
        return Alarmkey.query.filter_by(category=category).all()

    @staticmethod
    def getAlarmkeysByCategoryId(categoryid, keysetid=None):
        """
        Get all alarmkey definitions of given category id

        :param categoryid: category as string
        :param keysetid: keysetid as integer, 0 for un-matched, None for all
        :return: :py:class:`emonitor.modules.alarmkeys.alarmkey.Alarmkey` object list
        """
        key = Alarmkey.query.filter_by(id=categoryid).one()
        if keysetid is None:
            return Alarmkey.query.filter_by(category=key.category).all()
        elif int(keysetid) == 0:
            return Alarmkey.query.filter_by(category=key.category, _keyset=None).all()
        else:
            return Alarmkey.query.filter(Alarmkey.category == key.category and Alarmkey._keyset == keysetid).all()

    @staticmethod
    def getAlarmkeysDict():
        """
        Get dict of all alarmkeys with alarmkey.id as dict key
        :return: dict of alarmkeys
        """
        return dict(db.get(Alarmkey.id, Alarmkey).order_by(Alarmkey.key).all())

    @staticmethod
    def getDefault(department):
        """
        Get default alarmkey definition of given department

        :param department: id as integer
        :return: :py:class:`emonitor.modules.alarmkeys.alarmkey.Alarmkey` object
        """
        return AlarmkeyCars.query.filter_by(kid=9999, dept=department).first() or AlarmkeyCars(9999, department, '', '', '')
