import difflib
import re
import logging
import traceback
from collections import OrderedDict

import time
import datetime

from emonitor.modules.alarmkeys.alarmkey import Alarmkey
from emonitor.modules.alarms import AlarmFaxChecker
from emonitor.modules.streets import City
from emonitor.modules.streets import Street

__all__ = ['ILSFNSerialAlarmChecker']
logger = logging.getLogger(__name__)


class ILSFNSerialAlarmChecker(AlarmFaxChecker):
    __name__ = "ILSFN"
    __version__ = '0.1'

    fields = {}
    sections = OrderedDict()
    sections[u'Meldebild'] = (u'key', u'evalKey')
    sections[u'Ortsteil/Ort'] = (u'city', u'evalCity')
    sections[u'Stra\xdfe'] = (u'address', u'evalStreet')

    sections[u'Einsatznr'] = (u'time', u'evalTime')
    # sections[u'Hinweis'] = (u'remark', u'')

    def getEvalMethods(self):
        """get all eval methods of fax checker

        :return: list of names of eval methods
        """
        return [m for m in self.__class__.__dict__.keys() if m.startswith('eval')]

    @staticmethod
    def evalKey(fieldname, **params):
        if fieldname in ILSFNSerialAlarmChecker().fields:
            _str = ILSFNSerialAlarmChecker().fields[fieldname][0]
        else:  # key not found
            ILSFNSerialAlarmChecker().fields[fieldname] = (u'----', 0)
            raise
        if _str == '':
            ILSFNSerialAlarmChecker().fields[fieldname] = (_str, 0)
            return
        keys = {k.key: k.id for k in Alarmkey.getAlarmkeys()}
        try:
            repl = difflib.get_close_matches(_str.strip(), keys.keys(), 1, cutoff=0.8)  # default cutoff 0.6
            if len(repl) == 0:
                repl = difflib.get_close_matches(_str.strip(), keys.keys(), 1)  # try with default cutoff
            if len(repl) > 0:
                k = Alarmkey.getAlarmkeys(int(keys[repl[0]]))
                ILSFNSerialAlarmChecker().fields[fieldname] = (u'{}: {}'.format(k.category, k.key), k.id)
                ILSFNSerialAlarmChecker().logger.debug(u'key: found "{}: {}"'.format(k.category, k.key))
                return
            ILSFNSerialAlarmChecker().logger.info(u'key: "{}" not found in alarmkeys'.format(_str))
            ILSFNSerialAlarmChecker().fields[fieldname] = (_str, 0)
        except:
            ILSFNSerialAlarmChecker().logger.error(u'key: error in key evaluation')
        finally:
            return

    @staticmethod
    def evalTime(fieldname, **params):
        #if fieldname in ILSFNSerialAlarmChecker().fields:
        #    _rawTime = ILSFNSerialAlarmChecker().fields[fieldname][0]
        #else:
        t = datetime.datetime.now()
        #try:
        #    t = datetime.datetime.strptime(_rawTime, '%d.%m.%Y %H:%M:%S')
        #except ValueError:
        #    t = datetime.datetime.now()

        ILSFNSerialAlarmChecker().fields[fieldname] = (
        u'{}.{}.{} - {}:{}:00'.format(t.day, t.month, t.year, t.hour, t.minute), 1)

    @staticmethod
    def evalCity(fieldname, **params):
        if fieldname in ILSFNSerialAlarmChecker().fields:
            _str = ILSFNSerialAlarmChecker().fields[fieldname][0]
        else:  # city not found -> use default city
            city = City.getDefaultCity()
            ILSFNSerialAlarmChecker().fields[fieldname] = (city.name, city.id)
            raise

        alarmtype = params.get('alarmtype', None)
        if _str.strip() == '':
            ILSFNSerialAlarmChecker().fields[fieldname] = ('', 0)

        cities = City.getCities()
        for city in cities:  # test first word with defined subcities of cities
            try:
                repl = difflib.get_close_matches(_str.split()[0], city.subcities + [city.name], 1, cutoff=0.7)
                if len(repl) > 0:
                    ILSFNSerialAlarmChecker().fields[fieldname] = (repl[0], city.id)
                    return
            except:
                pass

        for city in cities:  # test whole string with subcities
            repl = difflib.get_close_matches(_str, city.subcities + [city.name], 1)
            if len(repl) > 0:
                ILSFNSerialAlarmChecker().fields[fieldname] = (repl[0], city.id)
                return

        if alarmtype.translation(u'_default_city_') in _str.lower():
            d_city = filter(lambda c: c.default == 1, cities)
            if len(d_city) == 1:
                ILSFNSerialAlarmChecker().fields[fieldname] = (d_city[0].name, d_city[0].id)
                return

            # use default city
            city = City.getDefaultCity()
            ILSFNSerialAlarmChecker().fields[fieldname] = (city.name, city.id)
            return

        if _str.startswith('in'):  # remove 'in' and plz
            _str = re.sub(r'in*|[0-9]*', '', _str[2:].strip())

            ILSFNSerialAlarmChecker().fields[fieldname] = (_str, 0)  # return original if no match
        return

    @staticmethod
    def evalStreet(fieldname, **params):
        alarmtype = params.get('alarmtype', None)
        options = params.get('options', [])

        streets = Street.getStreets()
        _str = ILSFNSerialAlarmChecker().fields[fieldname][0]
        if 'part' in options:  # addresspart, remove city names
            for c in City.getCities():
                if _str.endswith(c.name):
                    _str = _str.replace(c.name, '')
            pattern = re.compile(
                r'(?P<street>(^(\D+))) (?P<housenumber>(?P<hn>([0-9]{1,3}((\s?)[a-z])?)).*)'  # street with housenumber
                r'|((?P<streetname>((.*[0-9]{4})|(^(\D+)))))'
                r'|((?P<bab>((.*) (\>) )(?P<direction>(.*))))'  # highway
                r'|((.*) (?P<train>(KM .*).*))')  # train
        else:
            pattern = re.compile(
                r'(?P<street>(^(\D+))) (?P<housenumber>(?P<hn>([0-9]{1,3}((\s?)[a-z])?)).*)'  # street with housenumber
                r'|((?P<bab>A[0-9]{2,3} [A-Za-z]+) (?P<direction>(\D*))(( (?P<as>[0-9]*))|(.*)))'  # highway
                r'|((.*)(?P<train>(Bahnstrecke .*)) (?P<km>[0-9]+(.*)))'  # train
                r'|((?P<streetname>((.*[0-9]{4})|(^(\D+)))))'
            )

        m = pattern.match(_str)
        if m:
            if m.groupdict()['street'] or m.groupdict()[
                'streetname']:  # normal street, fields: 'street', 'housenumber' with sub 'hn'
                repl = difflib.get_close_matches(m.groupdict()['street'] or m.groupdict()['streetname'],
                                                 [s.name for s in streets], 1)
                if len(repl) > 0:
                    _streets = [s for s in filter(lambda s: s.name == repl[0], streets)]
                    if len(_streets) > 0:
                        if ILSFNSerialAlarmChecker().fields['city'][1] != 0:  # city given
                            for _s in _streets:  # find correct city
                                if _s.city.id == ILSFNSerialAlarmChecker().fields['city'][1]:
                                    _street = _s
                                    _streets = [_s]
                                    break
                            ILSFNSerialAlarmChecker().fields[fieldname] = (_street.name, _street.id)
                            ILSFNSerialAlarmChecker().logger.debug(
                                u'street: "{}" ({}) found'.format(_street.name, _street.id))
                        else:
                            ILSFNSerialAlarmChecker().fields[fieldname] = (
                            m.groupdict()['street'] or m.groupdict()['streetname'], 0)
                            if not re.match(alarmtype.translation(u'_street_'), _str[
                                1]) and 'part' not in options:  # ignore 'street' value and part-address
                                ILSFNSerialAlarmChecker().fields['streetno'] = (m.groupdict()['housenumber'], 0)

                    if m.groupdict()['hn'] and ILSFNSerialAlarmChecker().fields['city'][1] != 0:
                        if m.groupdict()['housenumber'] != m.groupdict()['housenumber'].replace('B', '6').replace(
                                u'\xdc', u'0'):
                            _housenumber = m.groupdict()['housenumber'].replace('B', '6').replace(u'\xdc', u'0')
                            _hn = _housenumber
                        else:
                            _housenumber = m.groupdict()['housenumber'].replace('B', '6').replace(u'\xdc', u'0')
                            _hn = m.groupdict()['hn']
                        if m.groupdict()['hn']:
                            db_hn = filter(lambda h: h.number.replace(' ', '') == _hn.replace(' ', ''),
                                           _streets[0].housenumbers)
                            if len(db_hn) == 0:
                                db_hn = filter(lambda h: h.number == _hn.split()[0], _streets[0].housenumbers)
                            if len(db_hn) > 0:
                                ILSFNSerialAlarmChecker().fields['id.streetno'] = (db_hn[0].number, db_hn[0].id)
                                ILSFNSerialAlarmChecker().fields['streetno'] = (_housenumber, db_hn[0].id)
                                ILSFNSerialAlarmChecker().fields['lat'] = (db_hn[0].points[0][0], db_hn[0].id)
                                ILSFNSerialAlarmChecker().fields['lng'] = (db_hn[0].points[0][1], db_hn[0].id)
                            elif _housenumber:
                                ILSFNSerialAlarmChecker().fields['streetno'] = (_housenumber, 0)
                                ILSFNSerialAlarmChecker().fields['lat'] = (_streets[0].lat, 0)
                                ILSFNSerialAlarmChecker().fields['lng'] = (_streets[0].lng, 0)
                            else:
                                ILSFNSerialAlarmChecker().fields['lat'] = (_streets[0].lat, 0)
                                ILSFNSerialAlarmChecker().fields['lng'] = (_streets[0].lng, 0)

            elif m.groupdict()['bab']:  # highway, fields: 'bab', 'direction', 'as'
                repl = difflib.get_close_matches(u"{} {}".format(m.groupdict()['bab'], m.groupdict()['direction']),
                                                 [s.name for s in streets], 1)
                if len(repl) > 0:
                    _streets = [s for s in filter(lambda s: s.name == repl[0], streets)]
                    if len(_streets) > 0:
                        _street = _streets[0]
                        ILSFNSerialAlarmChecker().fields[fieldname] = (_street.name, _street.id)
                        ILSFNSerialAlarmChecker().logger.debug(
                            u'street: "{}" ({}) found'.format(_street.name, _street.id))
                return

            elif m.groupdict()['train']:  # train, fields: 'train', 'km'
                repl = difflib.get_close_matches(m.groupdict()['train'], [s.name for s in streets], 1)
                if len(repl) > 0:
                    _streets = [s for s in filter(lambda s: s.name == repl[0], streets)]
                    if len(_streets) > 0:
                        _street = _streets[0]
                        ILSFNSerialAlarmChecker().fields[fieldname] = (_street.name, _street.id)
                        ILSFNSerialAlarmChecker().logger.debug(
                            u'street: "{}" ({}) found'.format(_street.name, _street.id))

                return

            else:  # not found
                repl = difflib.get_close_matches(_str, [s.name for s in streets])
                if len(repl) >= 1:
                    try:
                        street_id = u';'.join(
                            [u'{}'.format(s.id) for s in filter(lambda s: s.name == repl[0], streets)])
                    except:
                        street_id = u''

                        ILSFNSerialAlarmChecker().fields[fieldname] = (u'{}'.format(repl[0]), street_id)
                    if 'streetno' not in ILSFNSerialAlarmChecker().fields or ILSFNSerialAlarmChecker().fields[
                        'streetno'] == u"":
                        ILSFNSerialAlarmChecker().fields['streetno'] = (
                            u'{}'.format(u" ".join(_str[repl[0].count(u' ') + 1:])).replace(
                                alarmtype.translation(u'_street_'), u'').strip(), street_id)
                return
        else:
            ILSFNSerialAlarmChecker().fields[fieldname] = (_str, 0)
            return

    def buildAlarmFromText(self, alarmtype, rawtext):
        values = {}
        if alarmtype:
            sections = alarmtype.getSections()
            sectionnames = {s.name: s.key for s in sections}
            sectionmethods = {s.key: s.method for s in sections}
            ILSFNSerialAlarmChecker().fields['alarmtype'] = (alarmtype, 0)
        else:
            return values

        alarmmessage = re.search(b'\x02([\s\S]*)\x03', rawtext, re.MULTILINE)
        if alarmmessage:
            logger.info(u"Received valid alarmmessage from serial: {}".format(alarmmessage.groups()))
            strippedMessage = alarmmessage.group(1).strip()
            stringParts = strippedMessage.split(":")
            if len(stringParts) == 2:
                logger.info(u"Key: {}".format(stringParts[0]))
                ILSFNSerialAlarmChecker().fields['key'] = (stringParts[0], 0)
                addressParts = stringParts[1].split(",")
                if len(addressParts) == 5:
                    ILSFNSerialAlarmChecker().fields['city'] = (addressParts[0], 0)
                    ILSFNSerialAlarmChecker().fields['address'] = (addressParts[1], 0)
                    ILSFNSerialAlarmChecker().fields['addresspart'] = (addressParts[2], 0)
                    ILSFNSerialAlarmChecker().fields['remark'] = (addressParts[4], 0)

                else:
                    logger.error("Invalid message received")
            else:
                logger.error("Invalid message received")
        else:
            logger.info("Received invalid alarm message from serial")

        # uhrzeit = re.search(b'\x03([\s\S]*)\\r\\n', rawtext, re.MULTILINE | re.DOTALL)
        # if uhrzeit:
        #    #logger.info(u"Received valid datetime from serial {}".format(uhrzeit.group(1).strip()))
        #    ILSFNSerialAlarmChecker().fields['time'] = uhrzeit.group(1).strip()
        #ILSFNSerialAlarmChecker().fields['time'] = datetime.datetime.now()

        for section in sections:  # sections in order
            k = section.key
            if sectionmethods[k] != u'':
                method = sectionmethods[k].split(u';')[0]
                try:  # method parameters (optional)
                    method_params = sectionmethods[k].split(u';')[1]
                except:
                    method_params = ''

                # execute methods
                try:
                    getattr(self, method)(k, alarmtype=alarmtype,
                                          options=method_params.split(';'))  # fieldname, parameters
                except:
                    if u'error' not in values:
                        values['error'] = ''
                    values['error'] = u"".join((values['error'], u'error in method: {}\n'.format(method)))
                    ILSFNSerialAlarmChecker().logger.error(
                        u'error in section {} {}\n{}'.format(k, method, traceback.format_exc()))

        for k in ILSFNSerialAlarmChecker().fields:
            try:
                values[k] = (
                ILSFNSerialAlarmChecker().fields[k][0].decode('utf-8'), ILSFNSerialAlarmChecker().fields[k][1])
            except:
                values[k] = (ILSFNSerialAlarmChecker().fields[k][0], ILSFNSerialAlarmChecker().fields[k][1])
        return values
