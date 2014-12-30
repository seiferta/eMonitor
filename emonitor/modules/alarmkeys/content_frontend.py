from flask import request
from emonitor.extensions import classes


def getFrontendData(self, params={}):
    """
    Deliver frontend content of module alarmkeys

    :param params: given parameters of current request
    :return: data of alarmkeys
    """
    if request.args.get('action') == 'keyslookup':
        keys = {}

        for k in classes.get('alarmkey').getAlarmkeys():
            keys[str(k.id)] = '%s: %s' % (k.category, k.key)
        return keys

    elif request.args.get('action') == 'categorylookup':
        key = classes.get('alarmkey').getAlarmkeys(id=int(request.args.get('keyid')))
        return {'id': key.id, 'category': key.category}

    elif request.args.get('action') == 'carslookup':
        ret = {'cars1': [], 'cars2': [], 'material': []}
        try:
            city = classes.get('city').get_byid(int(request.args.get('cityid')))
        except ValueError:
            city = None
        key = classes.get('alarmkey').getAlarmkeys(id=int(request.args.get('keyid')))
        if request.args.get('objectid') != '0':  # use alarmobject and test for aao
            aobject = classes.get('alarmobject').getAlarmObjects(id=request.args.get('objectid'))
            if aobject.hasOwnAAO():
                return {'cars1': [c.id for c in aobject.getCars1()], 'cars2': [c.id for c in aobject.getCars2()],
                        'material': [m.id for m in aobject.getMaterial()]}
        if key and city:
            ret = {'cars1': [c.id for c in key.getCars1(city.dept)], 'cars2': [c.id for c in key.getCars2(city.dept)],
                   'material': [m.id for m in key.getMaterial(city.dept)]}
        return ret

    return ""
