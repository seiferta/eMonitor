import re
import xml.etree.ElementTree as ET
import datetime, time
import requests
from sqlalchemy import inspect
from flask import current_app
from emonitor.extensions import classes, events, signal, babel

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
    n = [n for n in self.street.housenumbers if str(n.number) == str(self.get('streetno').split(' ')[0])]
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


def getAlarmRoute(alarm):
    """
    get routing from webservice, points and description
    """
    params = {'format': 'kml', 'flat': classes.get('settings').get('homeLat'), 'flon': classes.get('settings').get('homeLng'), 'tlat': alarm.get('lat'), 'tlon': alarm.get('lng'), 'v': 'motorcar', 'fast': '1', 'layer': 'mapnik', 'instructions': '1', 'lang': current_app.config.get('BABEL_DEFAULT_LOCALE')}
    r = requests.get(alarm.ROUTEURL, params=params)
    tree = ET.fromstring(r.content)
    data = {}

    def getText(items, elementname):
        for el in items:
            elname = el.tag[el.tag.find('}') + 1:]
            if elname == elementname:
                return el.text

    def getElements(items, elementname):
        for el in items:
            elname = el.tag[el.tag.find('}') + 1:]
            if elname == elementname:
                return el

    elements = getElements(tree, 'Document')

    data['distance'] = float(getText(elements, 'distance'))
    data['traveltime'] = int(getText(elements, 'traveltime'))
    data['description'] = getText(elements, 'description')

    data['description'] = re.sub('\s+', ' ', data['description'].replace('\\', ''))
    description = []
    for l in data['description'].split('<br>'):
        if babel.gettext(u'alarms.print.bus') not in l.lower():
            match_dir = re.findall(r"" + babel.gettext(u'alarms.print.slightleft') + "|" + babel.gettext(u'alarms.print.left') + "|" + babel.gettext(u'alarms.print.slightright') + "|" +babel.gettext(u'alarms.print.right') + "|" + babel.gettext(u'alarms.print.straight') + "|\d\.\s" + babel.gettext(u'alarms.print.exit'), l.lower()),  # km extraction
            match_length = re.findall(r"\d*\.\d+\s*[k]?m|\d+\s*[k]?m", l)  # km extraction

            if len(match_dir) > 0 and len(match_length) > 0:
                try:
                    match_dir = re.sub('\d*\.|\s', '', match_dir[0][0].lower())  # reformat direction
                except IndexError:
                    continue
                direction = l.split('. Der Str')[0]
                if '[positive]' in direction or '[negative]' in direction or babel.gettext(u'alarms.print.highwaylong') in direction:  # eval highway
                    match_dir = 'highway'
                    direction = direction.replace(babel.gettext(u'alarms.print.highwaylong'), babel.gettext(u'alarms.print.highwayshort'))
                highwayexit = re.findall(r"auf .*;.*", l.lower())  # eval highway exit
                if len(highwayexit) > 0:
                    match_dir = 'highwayexit'
                    direction = direction.replace(babel.gettext(u'alarms.print.exitstart'), babel.gettext(u'alarms.print.exit').title()).replace(babel.gettext(u'alarms.print.straight'), babel.gettext(u'alarms.print.straightexit'))
                    direction = re.sub(';\s?', '/', direction)
                direction = direction.replace('[positive]', u'<b>%s</b>' % babel.gettext(u'alarms.print.positive'))
                direction = direction.replace('[negative]', u'<b>%s</b>' % babel.gettext(u'alarms.print.negative'))
                description.append([match_dir, match_length[0], direction])
    data['description'] = description

    f = getElements(getElements(elements, 'Folder'), 'Placemark')
    f = getElements(f, 'LineString')
    data['coordinates'] = []
    for c in getText(f, 'coordinates').split('\n'):
        if c.strip() != '':
            data['coordinates'].append((float(c.split(',')[0]), float(c.split(',')[1])))
    return data


def processFile(incomepath, filename):
    """
    run processing in test mode
    """
    params = dict(dict(incomepath=incomepath, filename=filename, mode='test'))
    handlers = events.getEvents('file_added').getHandlerList()
    dbhandlers = classes.get('eventhandler').getEventhandlers(event='file_added')
    for handler in dbhandlers:  # db
        for hdl in handlers:
            if handler.handler == hdl[0]:
                hdl[1]('file_added', params)
                res = []
                for p in handler.getParameterList():
                    try:
                        res.append('%s:%s' % (p, params[p.split('.')[1]].decode('utf-8')))
                    except:
                        if p.split('.')[1] in params.keys():
                            res = ['%s:%s' % (p, params[p.split('.')[1]])]
                            #params['error'] = '%s:%s' % (p, params[p.split('.')[1]])
                        else:
                            res = ['error: key not found - %s' % p.split('.')[1]]
                            params['error'] = 'error: key not found - %s' % p.split('.')[1]
                if u'error' in params.keys():
                    signal.send('alarm', 'testupload_start', result=res, handler=handler.handler.split('.')[-1], protocol=params['time'][-1], error=params['error'])
                else:
                    signal.send('alarm', 'testupload_start', result=res, handler=handler.handler.split('.')[-1], protocol=params['time'][-1])
    signal.send('alarm', 'testupload_start', result='done')