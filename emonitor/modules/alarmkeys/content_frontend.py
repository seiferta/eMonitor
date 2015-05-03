from flask import request
from emonitor.modules.alarmkeys.alarmkey import Alarmkey
from emonitor.modules.alarmobjects.alarmobject import AlarmObject
from emonitor.modules.streets.city import City


def getFrontendData(self, params={}):
    """
    Deliver frontend content of module alarmkeys

    :param params: given parameters of current request
    :return: data of alarmkeys
    """
    if request.args.get(u'action') == u'keyslookup':
        keys = {}

        for k in Alarmkey.getAlarmkeys():
            keys[u"{}".format(k.id)] = u'{}: {}'.format(k.category, k.key)
        return keys

    elif request.args.get(u'action') == u'categorylookup':
        key = Alarmkey.getAlarmkeys(id=request.args.get(u'keyid'))
        return {u'id': key.id, u'category': key.category}

    elif request.args.get(u'action') == u'carslookup':
        ret = {u'cars1': [], u'cars2': [], u'material': []}
        try:
            city = City.getCities(id=request.args.get(u'cityid'))
        except ValueError:
            city = None
        key = Alarmkey.getAlarmkeys(id=request.args.get(u'keyid'))
        if request.args.get(u'objectid') != u'0':  # use alarmobject and test for aao
            aobject = AlarmObject.getAlarmObjects(id=request.args.get(u'objectid'))
            if aobject.hasOwnAAO():
                return {u'cars1': [c.id for c in aobject.getCars1()], u'cars2': [c.id for c in aobject.getCars2()],
                        u'material': [m.id for m in aobject.getMaterial()]}
        if key and city:
            ret = {u'cars1': [c.id for c in key.getCars1(city.dept)], u'cars2': [c.id for c in key.getCars2(city.dept)],
                   u'material': [m.id for m in key.getMaterial(city.dept)]}
        return ret

    return u""
