import json
import glob
import re
import datetime
from flask import current_app
from emonitor.extensions import db


class AlarmkeySetBase:
    def __init__(self, filename, json_data, settype="integrated"):
        self.id = filename
        self.name = json_data.get('info').get('name')
        self.start = datetime.datetime.strptime(json_data.get('info').get('start'), '%Y-%m-%d')
        self.items = json_data.get('data')
        self.settype = settype


class AlarmkeySet(db.Model):
    """Alarmkeyset class"""
    __tablename__ = 'alarmkeysets'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), default='')
    base = db.Column(db.String(128), default='')
    startdate = db.Column(db.DATE)
    enddate = db.Column(db.DATE)
    remark = db.Column(db.Text)

    def __init__(self, name, base, startdate, enddate, remark):
        self.name = name
        self.base = base
        self.startdate = startdate
        self.enddate = enddate
        self.remark = remark

    @property
    def active(self):
        if (self.startdate or datetime.date.today()) <= datetime.date.today() <= (self.enddate or datetime.date.today()):
            return True
        return False

    @property
    def alarmkeys(self):
        base = AlarmkeySet.getBases(self.base)
        if len(base) == 1:
            return base[0].items
        else:
            return []

    def getDefinedKeys(self):
        from emonitor.modules.alarmkeys.alarmkey import Alarmkey
        return Alarmkey.getAlarmkeys(keysetid=self.id)

    def createBaseKeys(self):
        from emonitor.modules.alarmkeys.alarmkey import Alarmkey
        # get items for current key set
        items = Alarmkey.getOrphanKeys()
        result = [0, 0]  # updated / error items
        for k in self.alarmkeys:
            i = filter(lambda x: x.key == k.get('schlagwort') and x.category == k.get('stichwort'), items)
            if len(i) == 1:
                i[0]._keyset = self.id
                i[0].keysetitem = k.get('nr')
                result[0] += 1
            else:
                result[1] += 1
        db.session.commit()
        return result

    @staticmethod
    def getAlarmkeySets(id=0):
        """
        Get all alarmkeyset definitions or single definition with given 'id'

        :param keysetid: id of alarmkeyset
        :return: list of defintions or single definition
        """
        if id != 0:
            return AlarmkeySet.query.filter_by(id=int(id)).first()
        else:
            return AlarmkeySet.query.order_by('name').all()

    @staticmethod
    def getCurrentKeySet():
        """
        Get active :py:class:`emonitor.modules.alarmkeys.AlarmkeySet` depending in current date and AlarmkeySet attribute *startdate* and *enddate*

        :return: :py:class:`emonitor.modules.alarmkeys.AlarmkeySet` or *None*
        """
        for a in AlarmkeySet.getAlarmkeySets():
            if a.active:
                return a
        return None

    @staticmethod
    def getBases(basename=""):
        ret = []
        for b in glob.glob("emonitor/modules/alarmkeys/inc/*.json"):
            ret.append(AlarmkeySetBase(re.split(r'/|\\', b)[-1], json.load(open(b, 'r')), settype="integrated"))
        for b in glob.glob("{}alarmkeysetbase/*.json".format(current_app.config.get('PATH_DATA'))):
            ret.append(AlarmkeySetBase(re.split(r'/|\\', b)[-1], json.load(open(b, 'r')), settype="external"))
        if basename != "":
            return filter(lambda x: basename == x.id, ret)
        return ret
