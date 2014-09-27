from flask import request
from emonitor.extensions import classes


def getFrontendData(self):
    
    if request.args.get('action') == 'streetcoords':  # get map parameter for given alarmobjectid

        if request.args.get('id') != '':
            aobject = classes.get('alarmobject').getAlarmObjects(request.args.get('id'))
            if aobject.street:
                for hn in aobject.street.housenumbers:
                    if str(hn.number) == aobject.streetno.strip():
                        return dict(lat=map(lambda x: x[0], hn.points), lng=map(lambda x: x[1], hn.points), type='house')
            return dict(lat=aobject.lat, lng=aobject.lng, zoom=aobject.zoom, type='point')

    elif request.args.get('action') == 'alarmobject':  # get alarm object
        if request.args.get('id') != '':
            aobject = classes.get('alarmobject').getAlarmObjects(request.args.get('id'))

            return aobject.serialize
        return dict()
