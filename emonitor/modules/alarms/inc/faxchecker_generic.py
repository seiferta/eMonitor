import re
import difflib
import datetime
import ConfigParser
import traceback
from emonitor.lib.location import Location
from emonitor.modules.alarms.alarmutils import AlarmFaxChecker, AlarmFaxSection
from emonitor.modules.streets.street import Street
from emonitor.modules.streets.city import City
from emonitor.modules.settings.department import Department
from emonitor.modules.cars.car import Car
from emonitor.modules.alarmkeys.alarmkey import Alarmkey
from emonitor.modules.alarmobjects.alarmobject import AlarmObject


__all__ = ['GenericAlarmFaxChecker']


class GenericAlarmFaxChecker(AlarmFaxChecker):
    """Generic FaxChecker with generic regex implementation"""

    __name__ = "GENERIC (regex)"
    __version__ = '0.1'
    configtype = "generic"

    maxdist = 1500  # distance in meters
    fields = {}
    params = {}
    sections = []
    keywords = [u'sample']
    attributes = [u'divider', u'version']
    translations = AlarmFaxChecker.translations + [u'_bab_', u'_train_', u'_street_', u'_default_city_', u'_interchange_', u'_kilometer_', u'_train_identifier_']

    @staticmethod
    def _handleMultiline(value):
        """
        fix wordwrap of multiline messages
        :param value:
        :return:
        """
        v = []
        for line in value.split('\n'):
            line = line.replace('\r', '').strip()
            if re.match(r'^[A-Z0-9].*', line):  # newline if starts with upper char or digit
                v.append(line.strip())
            else:
                try:
                    v[-1] += line
                except IndexError:  # remark starts with lower case
                    v.append(line)
        return "\n".join(v)

    @staticmethod
    def evalTime(field, **params):
        field.value = ("{}:00".format(field.value[0].replace(' ', '-').replace('-', ' - ').replace('\xc3\x9c'.decode('utf-8'), '0')), 1)
        try:
            datetime.datetime.strptime(str(field.value[0]), '%d.%m.%Y - %H:%M:%S')
        except ValueError:
            field.value = (datetime.datetime.now().strftime('%d.%m.%Y - %H:%M:%S'), 1)

    @staticmethod
    def evalObject(field, **params):
        objects = AlarmObject.getAlarmObjects()
        repl = difflib.get_close_matches(field.value[0], [o.name for o in objects], 1)
        if repl:
            o = filter(lambda o: o.name == repl[0], objects)
            field.value = (repl[0], o[0].id)
            GenericAlarmFaxChecker().logger.debug(u'object: "{}" objectlist -> {}'.format(field.value[0], repl[0]))
        else:
            s = ""
            for p in field.value[0].split():  # try each char
                s += p
                repl = difflib.get_close_matches(s, [o.name for o in objects], 1)

                if len(repl) == 1:
                    o = filter(lambda o: o.name == repl[0], objects)
                    field.value = (repl[0], o[0].id)
                    GenericAlarmFaxChecker().logger.debug(u'object: "{}" special handling -> {}'.format(field.value[0], repl[0]))
                    return

    @staticmethod
    def evalKey(field, **params):
        if field.value[0] == '':
            return

        keys = {k.key: k.id for k in Alarmkey.getAlarmkeys()}
        try:
            repl = difflib.get_close_matches(field.value[0].strip(), keys.keys(), 1, cutoff=0.8)  # default cutoff 0.6
            if len(repl) == 0:
                repl = difflib.get_close_matches(field.value[0].strip(), keys.keys(), 1)  # try with default cutoff
            if len(repl) > 0:
                k = Alarmkey.getAlarmkeys(int(keys[repl[0]]))
                field.value = (u'{}: {}'.format(k.category, k.key), k.id)
                GenericAlarmFaxChecker().fields[field.key] = field.value
                GenericAlarmFaxChecker().logger.debug(u'key: found "{}: {}"'.format(k.category, k.key))
                return
            GenericAlarmFaxChecker().logger.info(u'key: "{}" not found in alarmkeys'.format(field.value[0]))
        except:
            GenericAlarmFaxChecker().logger.error(u'key: error in key evaluation')
        finally:
            return

    @staticmethod
    def evalMaterial(field, **params):
        cars = Car.getCars(params=['onlyactive'])
        carlist = [u'{} {}'.format(c.dept.name, c.name) for c in cars]
        c = [[], []]
        for p in [l for l in re.split(r"[\s]{2,}|[\n]+", field.value[0])]:
            addcar = None
            if len([d for d in Department.getDepartments() if d.name in p.strip()]) == 1:  # department default found
                c = [[u'default'] + c[0], [0] + c[1]]
                GenericAlarmFaxChecker().logger.debug(u'material: "{}" default department found'.format(p.strip()))
                continue

            # try list or car names
            repl = difflib.get_close_matches(p.strip(), carlist, 1, cutoff=0.7)
            if len(repl) == 1:
                addcar = filter(lambda x: u'{} {}'.format(x.dept.name, x.name) == repl[0], cars)[0]
                addcar = addcar.name, addcar.id

            else:  # try list of car descriptions
                descriptionlist = [u'{} {}'.format(cn.dept.name, cn.description) for cn in cars]
                repl = difflib.get_close_matches(p.strip(), descriptionlist, 1, cutoff=0.7)
                if len(repl) == 1:
                    addcar = filter(lambda x: u'{} {}'.format(x.dept.name, x.description) == repl[0], cars)[0]
                    addcar = addcar.name, addcar.id
                else:
                    t = ""
                    for x in p.split():  # try parts of name and stop after first match
                        t += x
                        repl = difflib.get_close_matches(t, carlist, 1, cutoff=0.7)
                        if len(repl) == 1:
                            addcar = filter(lambda x: u'{} {}'.format(x.dept.name, x.name) == repl[0], cars)[0]
                            addcar = addcar.name, addcar.id
                            break
            if addcar and addcar[1] not in c[1]:
                c[0].append(addcar[0])
                c[1].append(addcar[1])

        if len(c[0]) > 0:
            GenericAlarmFaxChecker().logger.debug(u'material: done with {}, {}'.format(c[0], c[1]))
            field.value = (u','.join(c[0]), u','.join([str(_c) for _c in c[1]]))

    @staticmethod
    def evalCity(field, **params):
        alarmtype = params.get('alarmtype', None)
        field.value = (field.value[0], -1)

        if field.value[0].strip() == '':
            field.value = ('', -1)

        cities = City.getCities()
        for city in cities:  # test first word with defined subcities of cities
            try:
                repl = difflib.get_close_matches(field.value[0].split()[0], city.subcities + [city.name], 1, cutoff=0.7)
                if len(repl) > 0:
                    field.value = (repl[0], city.id)
                    return
            except:
                pass

        for city in cities:  # test whole string with subcities
            repl = difflib.get_close_matches(field.value[0], city.subcities + [city.name], 1)
            if len(repl) > 0:
                field.value = (repl[0], city.id)
                return

        for s in field.value[0].split():
            for c in cities:
                repl = difflib.get_close_matches(s, [c.name], 1, cutoff=0.7)
                if len(repl) == 1:
                    field.value = (repl[0], c.id)
                    return

        if alarmtype.translation(u'_default_city_').lower() in field.value[0].lower():
            d_city = filter(lambda c: c.default == 1, cities)
            if len(d_city) == 1:
                field.value = (d_city[0].name, d_city[0].id)
                return

            # use default city
            city = City.getDefaultCity()
            field.value = (city.name, city.id)
            return

        if field.value[0].startswith('in'):  # remove 'in' and plz
            field.value = (re.sub(r'in*|[0-9]*', '', field.value[0][2:].strip()), field.value[1])

    @staticmethod
    def evalStreet(field, **params):
        alarmtype = params.get('alarmtype', None)
        options = params.get('options', [])
        streets = Street.getStreets()

        if 'part' in options:  # addresspart, remove city names
            for c in City.getCities():
                if field.value[0].endswith(c.name):
                    field.value = (field.value[0].replace(c.name, ''), field.value[1])
            pattern = re.compile(r'(?P<street>(^(\D+))) (?P<housenumber>(?P<hn>([0-9]{1,3}((\s?)[a-z])?)).*)'  # street with housenumber
                                 r'|((?P<streetname>((.*[0-9]{4})|(^(\D+)))))'
                                 r'|((?P<bab>((.*) (\>) )(?P<direction>(.*))))'  # highway
                                 r'|((.*) (?P<train>(KM .*).*))')  # train
        else:
            pattern = re.compile(r'(?P<street>(^(\D+))) (?P<housenumber>(?P<hn>([0-9]{1,3}((\s?)[a-z])?)).*)'  # street with housenumber
                                 r'|((?P<bab>A[0-9]{2,3} [A-Za-z]+) (?P<direction>(\D*))(( (?P<as>[0-9]*))|(.*)))'  # highway
                                 r'|((.*)(?P<train>(Bahnstrecke .*)) (?P<km>[0-9]+(.*)))'  # train
                                 r'|((?P<streetname>((.*[0-9]{4})|(^(\D+)))))'
                                 )

        m = pattern.match(field.value[0])
        if m:
            if m.groupdict().get('street') or m.groupdict().get('streetname'):  # normal street, fields: 'street', 'housenumber' with sub 'hn'
                repl = difflib.get_close_matches(m.groupdict()['street'] or m.groupdict()['streetname'], [s.name for s in streets], 1)
                if len(repl) > 0:
                    _streets = [s for s in filter(lambda s: s.name == repl[0], streets)]
                    if len(_streets) > 0:
                        field.value = (_streets[0].name, _streets[0].id)
                        if not re.match(alarmtype.translation(u'_street_'), field.value[0][1]) and 'part' not in options:  # ignore 'street' value and part-address
                            GenericAlarmFaxChecker().fields['streetno'] = (m.groupdict()['housenumber'], 0)

                    if m.groupdict()['hn'] and GenericAlarmFaxChecker().fields.get('city', ('', 0))[1] != 0:
                        if m.groupdict()['housenumber'] != m.groupdict()['housenumber'].replace('B', '6').replace(u'\xdc', u'0'):
                            _housenumber = m.groupdict()['housenumber'].replace('B', '6').replace(u'\xdc', u'0')
                            _hn = _housenumber
                        else:
                            _housenumber = m.groupdict()['housenumber'].replace('B', '6').replace(u'\xdc', u'0')
                            _hn = m.groupdict()['hn']
                        if m.groupdict()['hn']:
                            db_hn = filter(lambda h: h.number.replace(' ', '') == _hn.replace(' ', ''), _streets[0].housenumbers)
                            if len(db_hn) == 0:
                                db_hn = filter(lambda h: h.number == _hn.split()[0], _streets[0].housenumbers)
                            if len(db_hn) > 0:
                                GenericAlarmFaxChecker().fields.update({'id.streetno': (db_hn[0].number, db_hn[0].id), 'streetno': (_housenumber, db_hn[0].id), 'lat': (db_hn[0].points[0][0], db_hn[0].id), 'lng': (db_hn[0].points[0][1], db_hn[0].id)})
                            elif _housenumber:
                                GenericAlarmFaxChecker().fields.update({'streetno': (_housenumber, 0), 'lat': (_streets[0].lat, 0), 'lng': (_streets[0].lng, 0)})
                            else:
                                GenericAlarmFaxChecker().fields.update({'lat': (_streets[0].lat, 0), 'lng': (_streets[0].lng, 0)})
                else:
                    repl = difflib.get_close_matches(field.value[0], [s.name for s in streets], 1)
                    if len(repl) > 0:
                        _streets = [s for s in filter(lambda s: s.name == repl[0], streets)]
                        if len(_streets) > 0:
                            field.value = (_streets[0].name, _streets[0].id)
            elif m.groupdict()['bab']:  # highway, fields: 'bab', 'direction', 'as'
                repl = difflib.get_close_matches(u"{} {}".format(m.groupdict()['bab'], m.groupdict()['direction']), [s.name for s in streets], 1)
                if len(repl) > 0:
                    _streets = [s for s in filter(lambda s: s.name == repl[0], streets)]
                    if len(_streets) > 0:
                        _street = _streets[0]
                        field.value = (_street.name, _street.id)
                        GenericAlarmFaxChecker().logger.debug(u'street: "{}" ({}) found'.format(_street.name, _street.id))
                return

            elif m.groupdict()['train']:  # train, fields: 'train', 'km'
                repl = difflib.get_close_matches(m.groupdict()['train'], [s.name for s in streets], 1)
                if len(repl) > 0:
                    _streets = [s for s in filter(lambda s: s.name == repl[0], streets)]
                    if len(_streets) > 0:
                        _street = _streets[0]
                        field.value = (_street.name, _street.id)
                        GenericAlarmFaxChecker().logger.debug(u'street: "{}" ({}) found'.format(_street.name, _street.id))

            else:  # not found
                repl = difflib.get_close_matches(field.value[0], [s.name for s in streets])
                if len(repl) >= 1:
                    try:
                        street_id = u';'.join([u'{}'.format(s.id) for s in filter(lambda s: s.name == repl[0], streets)])
                    except:
                        street_id = u''
                    field.value = (u'{}'.format(repl[0]), street_id)
                    if 'streetno' not in GenericAlarmFaxChecker().fields or GenericAlarmFaxChecker().fields['streetno'] == u"":
                        GenericAlarmFaxChecker().fields['streetno'] = (u'{}'.format(u" ".join(field.value[0][repl[0].count(u' ') + 1:])).replace(alarmtype.translation(u'_street_'), u'').strip(), street_id)

    @staticmethod
    def evalAddressPart(field, **params):
        alarmtype = params.get('alarmtype', None)
        options = params.get('options', [])
        _str = field.value[0]
        field.value = (_str, 0)
        options.append('part')
        params['options'] = filter(None, options)
        GenericAlarmFaxChecker().evalStreet(field, **params)
        GenericAlarmFaxChecker().fields[field.key] = field.value  # do not remove

        if _str.endswith(')') and alarmtype.translation(u'_interchange_') in _str:  # bab part found
            part = '{}'.format(_str[_str.rfind('(') + 1:-1].replace(u'\n', u' '))
            field.value = (u'{}: {}'.format(alarmtype.translation(u'_kilometer_'), part), -1)
            if GenericAlarmFaxChecker().fields['address'][1] != 0:
                _streets = Street.getStreets(id=GenericAlarmFaxChecker().fields['address'][1])
                numbers = _streets.housenumbers
                hn = difflib.get_close_matches(part, [n.number for n in numbers], 1)
                GenericAlarmFaxChecker().fields['zoom'] = (u'14', 1)
                if len(hn) == 1:
                    nr = [n for n in numbers if n.number == hn[0]][0]
                    GenericAlarmFaxChecker().fields.update({'streetno': (nr.number, nr.id), 'id.streetno': (nr.id, nr.id), 'lat': (nr.points[0][0], nr.id), 'lng': (nr.points[0][1], nr.id)})
                return

        elif alarmtype.translation(u'_train_identifier_') in _str:  # found train position
            part = u'{}'.format(_str[_str.find(alarmtype.translation(u'_train_identifier_')):])
            field.value = (u'{}'.format(part), 1)
            numbers = Street.getStreets(id=GenericAlarmFaxChecker().fields['address'][1]).housenumbers

            for nr in numbers:
                if part.startswith(nr.number):
                    GenericAlarmFaxChecker().fields.update({'streetno': (nr.number, nr.id), 'id.streetno': (nr.id, nr.id), 'lat': (nr.points[0][0], nr.id), 'lng': (nr.points[0][1], nr.id), 'zoom': (u'15', 1)})
                    return
        else:
            if field.value[1] != 0:
                return
            part = _str
        field.value = (part, -1)

    @staticmethod
    def evalPosition(field, **params):
        position = {'lat': 0, 'lng': 0, 'type': 'GK'}
        for f in re.split(r'GK4 (?:([X|Y].[\d|\.]+))|(?:([X|Y].\s+\d+))', field.value[0]):
            if not f:
                continue
            if f.startswith('X'):
                position['lat'] = f.replace('X:', '').strip()
            elif f.startswith('Y'):
                position['lng'] = f.replace('Y:', '').strip()
            elif f.startswith('GK'):
                position['type'] = 'GK'
        location = Location(position['lat'], position['lng'], geotype='gk')

        if GenericAlarmFaxChecker.fields.get('lat') and GenericAlarmFaxChecker.fields.get('lng'):
            _lat = GenericAlarmFaxChecker.fields.get('lat')
            _lng = GenericAlarmFaxChecker.fields.get('lng')
            if location.getDistance(_lat[0], _lng[0]) > GenericAlarmFaxChecker.maxdist:
                GenericAlarmFaxChecker().logger.info('distance street -> fax {} m'.format(location.getDistance(_lat[0], _lng[0])))
                position['lat'], position['lng'] = location.getLatLng()
        else:
            _lat, _lng = location.getLatLng()
            GenericAlarmFaxChecker.fields[u'lat'] = (_lat, 1)
            GenericAlarmFaxChecker.fields[u'lng'] = (_lng, 1)
            position[u'lat'], position[u'lng'] = _lat, _lng
        field.value = ("{lat};{lng};{type}".format(**position), 1)

    @staticmethod
    def evalAlarmplan(field, **params):
        if field.value[0].strip() != "":
            field.value = (field.value[0].replace(u'B', u'6').strip(), 1)

    @staticmethod
    def evalRemark(field, **params):
        field.value = (GenericAlarmFaxChecker._handleMultiline(field.value[0]), field.value[1])

    def loadConfig(self, **params):
        _cfg = ConfigParser.ConfigParser()
        GenericAlarmFaxChecker().sections = []
        if params.get('config', None):  # no config given
            _cfg.readfp(params.get('config', None))
        elif params.get('configstring', None):
            import StringIO
            _cfg.readfp(StringIO.StringIO(params.get('configstring', '')))
        else:
            return

        for section in _cfg.sections():
            if section == 'global':  # global parameters
                GenericAlarmFaxChecker().translations = _cfg.get('global', 'translations')
                for p in [param for param in _cfg.options(section) if param not in ['translations']]:
                    GenericAlarmFaxChecker().params[p] = _cfg.get(section, p)
                continue
            _params = {}
            for p in [param for param in _cfg.options(section) if param not in ['start', 'end']]:
                _params[p] = _cfg.get(section, p)
            GenericAlarmFaxChecker().sections.append(AlarmFaxSection(section, _cfg.get(section, 'start'), _cfg.get(section, 'end'), **_params))
        self.logger.debug('config loaded')

    def getEvalMethods(self):
        return [m for m in self.__class__.__dict__.keys() if m.startswith('eval')]

    def buildAlarmFromText(self, alarmtype, rawtext):
        self.loadConfig(configstring=alarmtype.getConfigFile())
        self.logger.info('start eval text')
        _evalerror = []

        for section in GenericAlarmFaxChecker().sections:
            try:
                section.value = ('', 0)
                if section.params.get('multiline'):
                    pattern = re.compile(section.getRegEx(**GenericAlarmFaxChecker().params), re.DOTALL)
                else:
                    pattern = re.compile(section.getRegEx(**GenericAlarmFaxChecker().params), re.MULTILINE)
                m = re.findall(pattern, rawtext)
                self.logger.info(u"{}: {}".format(section.key, section.getRegEx(**GenericAlarmFaxChecker().params)))

                if m:
                    try:
                        section.value = (" ".join([v.replace('\r', '').strip() for v in m if v.strip() != '']), 0)
                    except AttributeError:
                        section.value = (" ".join([v.replace('\r', '').strip() for v in m[0] if v.strip() != '']), 0)
                    if section.params.get('multiline'):
                        if section.params.get('method') != '':
                            section.value = (section.value[0], section.value[1])
                        else:
                            section.value = (GenericAlarmFaxChecker._handleMultiline(section.value[0]), section.value[1])

                    if section.params.get('method'):
                        getattr(self, str(section.params.get('method')))(section, alarmtype=alarmtype)
                    self.logger.debug(u'[{:12s}]: {}'.format(section.key, section.value))
                else:
                    self.logger.debug(u'[{:12s}]: eval with no value'.format(section.key))
                    _evalerror.append(section.key)
            except:
                GenericAlarmFaxChecker().fields['error'] = GenericAlarmFaxChecker().fields.get('error', '') + traceback.format_exc() + "<br>"

            GenericAlarmFaxChecker().fields[section.key] = section.value
        self.logger.info(u'eval text done for {} field(s) with {} error(s)'.format(len(GenericAlarmFaxChecker().sections), len(_evalerror)))
        if len(_evalerror) > 0:
            self.logger.error(u'error in eval field(s): {}'.format(u','.join(_evalerror)))
        v = GenericAlarmFaxChecker().fields
        v.update({section.key: section.value for section in GenericAlarmFaxChecker().sections})
        return v
