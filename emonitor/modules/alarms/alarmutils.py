import re
import datetime, time
from sqlalchemy import inspect
from emonitor.extensions import classes
import difflib

__all__ = ['evalStreet', 'evalMaterial', 'evalTime', 'evalObject', 'evalAlarmplan', 'evalCity', 'evalAddressPart', 'evalKey', 'getEvalMethods', 'buildAlarmFromText']


# helper methods for object attributes
def get_street_proto(self, stype):  # deliver street object
    _t = {1: 'address', 2: 'address2'}
    if self.get('id.%s' % _t[stype]) and self.get('id.%s' % _t[stype], '0') not in ['-1', '0']:
        return classes.get('street').getStreet(int(self.get('id.%s' % _t[stype], '0')))
    else:
        return classes.get('street')(self.get(_t[stype], ''), '', '', 1, '', float(classes.get('settings').get('defaultLat', '0')), float(classes.get('settings').get('defaultLng', '0')), float(classes.get('settings').get('defaultZoom', '13')), 1)


def get_street(self):
    return get_street_proto(self, 1)


def get_housenumber(self):
    number = self.get('streetno').split(' ')[0]
    n = [n for n in self.street.housenumbers if str(n.number) == str(number)]
    if len(n) == 1:
        return n[0]
    else:
        return None


def get_street2(self):
    return get_street_proto(self, 2)


def get_streetno(self):
    return self.get('streetno', '')


def get_endtimestamp(self):
    try:
        if self.get('endtimestamp') == '':
            return datetime.datetime.fromtimestamp(float(time.time()))
        else:
            return datetime.datetime.fromtimestamp(float(self.get('endtimestamp')))
    except:
        return datetime.datetime.fromtimestamp(float(time.time()))


def get_object(self):
    if not inspect(self).session:
        return None
    objs = inspect(self).session.query(classes.get('alarmobject'))
    if self.get('id.object') and self.get('id.object') != '0':
        return objs.filter_by(id=int(self.get('id.object'))).first()
    else:
        if self.get('object'):
            return classes.get('alarmobject')(self.get('object'), 0, '', '', '', '', self.get('alarmplan'), 0)
        return None


def get_cars_proto(self, ctype):
    # type 1:cars1, 2:cars2, 3:material
    _t = {1: 'k.cars1', 2: 'k.cars2', 3: 'k.material'}
    ret = []
    if not inspect(self).session:
        return ret
    #cars = inspect(self).session.query(classes.get('car').car.Car)
    cars = classes.get('car').getCars()
    for _c in [int(c) for c in self.get(_t[ctype], []).split(',') if c != '']:
        try:
            ret.append(filter(lambda c: c.id == _c, cars)[0])
        except IndexError:
            pass
    return ret


def get_cars1(self):
    return get_cars_proto(self, 1)


def get_cars2(self):
    return get_cars_proto(self, 2)


def get_material(self):
    return get_cars_proto(self, 3)


def get_key(self):  # deliver alarmkey object
    if self.get('id.key') and self.get('id.key') not in ['None', '0']:
        return classes.get('alarmkey').getAlarmkeys(self.get('id.key'))
    else:
        k = classes.get('alarmkey')(u'', '%s' % self._key, u'', u'-not in list-')
        k.id = 0
        return k


def get_city(self):  # deliver city object
    if not inspect(self).session:
        return classes.get('city')(self.get('city', ''), 1, 'osmap', 0, '', '', 0)
    if self.get('id.city') and self.get('id.city') != '0':  # city found
        return classes.get('city').get_byid(self.get('id.city'))
    elif self.get('id.city', '0') == '0':  # not in list
        return classes.get('city')(self.get('city', ''), 1, 'osmap', 0, '', '', 0)
    else:
        return classes.get('city').getDefaultCity()


def get_person(self):  # deliver person string
    return self.get('person', '')


def get_priority(self):  # deliver priority integer
    return int(self.get('priority', '1'))  # normal
    

def get_remark(self):  # deliver remark string
    return self.get('remark', '')
    

def get_lat(self):  # deliver lat float
    return float(self.get('lat', classes.get('settings').settings.Settings.get('defaultLat', '0')))


def get_lng(self):  # deliver lng float
    return float(self.get('lng', classes.get('settings').settings.Settings.get('defaultLng', '0')))


def get_zoom(self):  # deliver zoom  integer
    return int(self.get('zoom', classes.get('settings').settings.Settings.get('defaultZoom', '13')))


def get_marker(self):  # deliver markerinfo: 0=no marker
    return int(self.get('marker', '0'))


class AlarmFaxChecker:
    __name__ = "alarmfaxproto"

    def __init__(self):
        pass

    def getEvalMethods(self):
        return []

    def buildAlarmFromText(self, alarmtype, rawtext):
        return dict()