from flask import request
from emonitor.extensions import classes


def getFrontendContent(self, params={}):  # not needed: module used by locations module
    return "...."
    
    
def getFrontendData(self):
    
    if request.args.get('action') == 'streetcoords':  # get map parameter for given alarmobjectid

        if request.args.get('id') != '':
            aobject = classes.get('alarmobject').getAlarmObjects(request.args.get('id'))
            return dict(lat=aobject.lat, lng=aobject.lng, zoom=aobject.zoom)
