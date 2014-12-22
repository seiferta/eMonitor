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
            #keys[str(k.id)] = '%s' %(k.category, k.key)
        return keys
        
    elif request.args.get('action') == 'categorylookup':
        key = classes.get('alarmkey').getAlarmkeys(id=int(request.args.get('keyid')))
        return {'id': key.id, 'category': key.category}

    elif request.args.get('action') == 'carslookup':
        city = None
        ret = {'cars1': [], 'cars2': [], 'material': []}
        try:
            city = classes.get('city').get_byid(int(request.args.get('cityid')))
        except ValueError:
            city = None
        key = classes.get('alarmkey').getAlarmkeys(id=int(request.args.get('keyid')))
        if key and city:
            ret = {'cars1': [c.id for c in key.getCars1(city.dept)], 'cars2': [c.id for c in key.getCars2(city.dept)],
                   'material': [m.id for m in key.getMaterial(city.dept)]}
        return ret
        
    return ""
