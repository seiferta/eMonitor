from flask import request
from emonitor.modules.alarmobjects.alarmobject import AlarmObject


def getFrontendData(self):
    """
    Deliver frontend content of module alarmobjects (ajax)

    :return: data of alarmobjects
    """
    if request.args.get('action') == 'streetcoords':  # get map parameter for given alarmobjectid

        if request.args.get('id') != '':
            aobject = AlarmObject.getAlarmObjects(request.args.get('id'))
            if aobject.street:
                points = dict(lat=[], lng=[], type='house')

                hn = aobject.street.getHouseNumber(number=aobject.streetno.strip())
                #for hn in aobject.street.housenumbers:
                #    if str(hn.number) == aobject.streetno.strip():
                points['lat'].extend(map(lambda x: x[0], hn.points))
                points['lng'].extend(map(lambda x: x[1], hn.points))
                if len(points['lat']) > 0:  # house number found
                    return points
            return dict(lat=aobject.lat, lng=aobject.lng, zoom=aobject.zoom, type='point')

    elif request.args.get('action') == 'alarmobject':  # get alarm object
        if request.args.get('id') != '':
            aobject = AlarmObject.getAlarmObjects(request.args.get('id'))
            if aobject:
                return aobject.serialize
        return dict()
