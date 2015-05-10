import re
import xml.etree.ElementTree as ET
import logging
import datetime, time
import requests
import json
from collections import OrderedDict
from sqlalchemy import inspect
from flask import current_app
from emonitor.extensions import events, signal, babel
from emonitor.widget.monitorwidget import MonitorWidget
from emonitor.modules.alarmobjects.alarmobject import AlarmObject
from emonitor.modules.alarmkeys.alarmkey import Alarmkey
from emonitor.modules.cars.car import Car
from emonitor.modules.streets.city import City
from emonitor.modules.streets.housenumber import Housenumber
from emonitor.modules.events.eventhandler import Eventhandler
from emonitor.modules.streets.street import Street
from emonitor.modules.settings.settings import Settings


# helper methods for object attributes
def get_street_proto(self, stype):  # deliver street object
    _t = {1: 'address', 2: 'address2'}
    if self.get('id.%s' % _t[stype]) and self.get('id.%s' % _t[stype], '0') not in ['-1', '0']:
        return Street.getStreets(id=self.get('id.%s' % _t[stype], '0'))
    else:
        return Street(self.get(_t[stype], ''), '', '', 1, '', float(Settings.get('defaultLat', '0')), float(Settings.get('defaultLng', '0')), float(Settings.get('defaultZoom', '13')), 1)


def set_street_proto(self, value, stype):
    _t = {1: 'address', 2: 'address2'}
    if value and value.id and value.name:
        self.set("id.{}".format(_t[stype]), value.id)
        self.set("{}".format(_t[stype]), value.name)


def get_street(self):
    return get_street_proto(self, 1)


def set_street(self, value):
    set_street_proto(self, value, 1)


def get_housenumber(self):
    if self.get('id.streetno', '') != '':
        return Housenumber.getHousenumbers(self.get('id.streetno'))
    try:
        n = [n for n in self.street.housenumbers if u'{}'.format(n.number) == self.get('streetno').split(' ')[0]]
        if len(n) == 1:
            return n[0]
        else:
            return None
    except:
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
    objs = inspect(self).session.query(AlarmObject)
    if self.get('id.object') and self.get('id.object') != '0':
        return objs.filter_by(id=int(self.get('id.object'))).first()
    else:
        if self.get('object'):
            return AlarmObject(self.get('object'), 0, '', '', '', '', self.get('alarmplan'), 0, '', 0, 0)
        return None


def set_object(self, alarmobject):
    self.set('id.object', alarmobject.id)
    self.set('object', alarmobject.name)


def get_cars_proto(self, ctype):
    # type 1:cars1, 2:cars2, 3:material
    _t = {1: 'k.cars1', 2: 'k.cars2', 3: 'k.material'}
    ret = []
    if not inspect(self).session:
        return ret
    cars = Car.getCars()
    for _c in [int(c) for c in self.get(_t[ctype], '').split(',') if c != '']:
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


def set_material(self, material):
    for t in ('cars1', 'cars2', 'material'):
        if t in material:
            self.set(u"k.{}".format(t), material[t])


def get_key(self):  # deliver alarmkey object
    if self.get('id.key') and self.get('id.key') not in ['None', '0']:
        return Alarmkey.query.filter_by(id=self.get('id.key')).scalar()
    else:
        k = Alarmkey(u'', u'%s' % self._key, u'', u'-not in list-')
        k.id = 0
        return k


def get_city(self):  # deliver city object
    if self.get('id.city', '0') != '0':  # city found
        return City.getCities(id=self.get('id.city'))
    elif self.get('id.city', '0') == '0':  # not in list
        return City(self.get('city', ''), 1, 'osmap', 0, '', '', 0, '')
    else:
        return City.getDefaultCity()


def set_city(self, city):  # set city parameters from object
    if city:
        self.set('id.city', city.id)
        self.set('city', city.name)
    else:
        self.set('id.city', '')
        self.set('city', '')


def get_person(self):  # deliver person string
    return self.get('person', '')


def get_priority(self):  # deliver priority integer
    return int(self.get('priority', '1'))  # normal
    

def get_remark(self):  # deliver remark string
    return self.get('remark', '')
    

def get_lat(self):  # deliver lat float
    return float(self.get('lat', Settings.get('defaultLat', '0')))


def get_lng(self):  # deliver lng float
    return float(self.get('lng', Settings.get('defaultLng', '0')))


def get_zoom(self):  # deliver zoom  integer
    return int(self.get('zoom', Settings.get('defaultZoom', '13')))


def get_marker(self):  # deliver markerinfo: 0=no marker
    return int(self.get('marker', '0'))


def get_position(self):
    """
    Return position as dict

    :return: dict with lat, lng, zoom
    """
    return dict(lat=get_lat(self), lng=get_lng(self), zoom=get_zoom(self))


def set_position(self, position):
    """
    Set position (lat, lng, zoom)

    :param position: dict with keys: lat, lng, zoom
    """
    if 'lat' in position:
        self.set('lat', position['lat'])
    if 'lng' in position:
        self.set('lng', position['lng'])
    if 'zoom' in position:
        self.set('zoom', position['zoom'])
    else:
        self.set('zoom', 17)


class AlarmFaxChecker:
    """
    Prototype for fax checkers
    """
    __name__ = "alarmfaxproto"
    translations = [u'_bma_main_', u'_bma_key_', u'_bma_']  # default parameters needed for alarm generation
    sections = OrderedDict()
    keywords = {}

    def __init__(self):
        logging.basicConfig()
        self.logger = logging.getLogger('emonitor.modules.alarms.faxchecker.{}'.format(self.__name__))
        self.loglevel = logging.ERROR
        self.logger.setLevel(self.loglevel)

    def getId(self):
        """
        Get attributename *__name__* of faxchecker class

        .. note:: removes *space* and *.*
        """
        return self.__name__.replace('.', '').replace(' ', '')

    def getEvalMethods(self):
        """
        Get list of all eval methods of current faxchecker

        :return: list of methods
        """
        return []

    def getDefaultConfig(self):
        """
        Get dict with default configuration of faxchecker

        :return: dict
        """
        return {u'keywords': self.keywords, u'sections': self.sections, u'translations': self.translations}

    def buildAlarmFromText(self, alarmtype, rawtext):
        """
        Build attributes from text input

        :return: dict with alarm fields/values
        """
        return dict()


def getAlarmRoute(alarm):
    """
    get routing from webservice, points and description
    """
    if alarm.get('lat', '') != '':
        params = {'format': 'kml', 'flat': Settings.get('homeLat'), 'flon': Settings.get('homeLng'), 'tlat': alarm.get('lat'), 'tlon': alarm.get('lng'), 'v': 'motorcar', 'fast': '1', 'layer': 'mapnik', 'instructions': '1', 'lang': current_app.config.get('BABEL_DEFAULT_LOCALE')}
    else:
        params = {'format': 'kml', 'flat': Settings.get('homeLat'), 'flon': Settings.get('homeLng'), 'tlat': 0, 'tlon': 0, 'v': 'motorcar', 'fast': '1', 'layer': 'mapnik', 'instructions': '1', 'lang': current_app.config.get('BABEL_DEFAULT_LOCALE')}
        if alarm.object:
            params.update({'tlat': alarm.object.lat, 'tlon': alarm.object.lng})
    try:
        r = requests.get(alarm.ROUTEURL, params=params)
        tree = ET.fromstring(r.content)
    except:
        return {}
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
    if data['description'] is None:
        data['description'] = ""
        data['error'] = 1

    data['description'] = re.sub('\s+', ' ', data['description'].replace('\\', ''))
    description = []
    for l in data['description'].split('<br>'):
        if babel.gettext(u'alarms.print.bus') not in l.lower():
            match_dir = re.findall(r"" + babel.gettext(u'alarms.print.slightleft') + "|" + babel.gettext(u'alarms.print.left') + "|" + babel.gettext(u'alarms.print.slightright') + "|" + babel.gettext(u'alarms.print.right') + "|" + babel.gettext(u'alarms.print.straight') + "|\d\.\s" + babel.gettext(u'alarms.print.exit'), l.lower()),  # km extraction
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
    params = dict(incomepath=incomepath, filename=filename, mode='test')
    handlers = events.getEvents('file_added').getHandlerList()
    dbhandlers = Eventhandler.getEventhandlers(event='file_added')
    for handler in dbhandlers:  # db
        for hdl in handlers:
            if handler.handler == hdl[0]:
                #p = hdl[1]('file_added', params)
                params.update(hdl[1]('file_added', **params))
                res = []
                for p in handler.getParameterList():
                    try:
                        res.append(u'{}:{}'.format(p, params[p.split('.')[1]]))
                    except:
                        try:
                            if p.split(u'.')[1] in params.keys():
                                res = [u'{}:{}'.format(p, params[p.split('.')[1]])]
                            else:
                                res = [u'error: key not found - {}'.format(p.split('.')[1])]
                                params['error'] = u'error: key not found - {}'.format(p.split('.')[1])
                        except:
                            import traceback
                            print traceback.format_exc()
                if u'error' in params.keys():
                    signal.send('alarm', 'testupload_start', result=res, handler=handler.handler.split('.')[-1], protocol=params['time'][-1], error=params['error'])
                else:
                    signal.send('alarm', 'testupload_start', result=res, handler=handler.handler.split('.')[-1], protocol=params['time'][-1])
    signal.send('alarm', 'testupload_start', result='done')
    return params


class AlarmRemarkWidget(MonitorWidget):
    template = "widget.alarm_comment.html"
    size = (2, 1)

    def addParameters(self, **kwargs):
        self.params.update(kwargs)


class AlarmWidget(MonitorWidget):
    template = 'widget.alarm.html'
    size = (2, 1)

    def addParameters(self, **kwargs):
        self.params.update(kwargs)


class AlarmIncomeWidget(MonitorWidget):
    template = 'widget.income.html'
    size = (2, 2)

    def addParameters(self, **kwargs):
        self.params.update(kwargs)


class AlarmTimerWidget(MonitorWidget):
    template = 'widget.timer.html'
    size = (1, 1)

    def addParameters(self, **kwargs):
        self.params.update(kwargs)
