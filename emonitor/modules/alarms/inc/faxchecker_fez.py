from collections import OrderedDict
import re
import difflib
from emonitor.modules.alarms.alarmutils import AlarmFaxChecker
from emonitor.modules.streets.street import Street
from emonitor.modules.streets.city import City
from emonitor.modules.cars.car import Car
from emonitor.modules.settings.department import Department
from emonitor.modules.alarmkeys.alarmkey import Alarmkey
from emonitor.modules.alarmobjects.alarmobject import AlarmObject

__all__ = ['FezAlarmFaxChecker']


class FezAlarmFaxChecker(AlarmFaxChecker):
    """
    fax checker implementation for Feuerwehreinsatzzentrale Muenchen Land (FEZ) with special layout
    """
    __name__ = "FEZ"
    __version__ = '0.2'

    fields = {}
    sections = OrderedDict()
    sections[u'Alarmschreiben'] = (u'', u'')
    sections[u'Telefon'] = (u'', u'')
    sections[u'Einsatznr'] = (u'time', u'evalTime')
    sections[u'Alarm'] = (u'', u'')
    sections[u'Mitteiler'] = (u'person', u'')
    sections[u'Einsatzort'] = (u'', u'')
    sections[u'Ortsteil/Ort'] = (u'city', u'evalCity')
    sections[u'Stra\xdfe'] = (u'address', u'evalStreet')
    sections[u'Abschnitt'] = (u'addresspart', u'evalAddressPart')
    sections[u'Kreuzung'] = (u'crossing', u'')
    sections[u'Objekt'] = (u'object', u'evalObject')
    sections[u'Einsatzplan'] = (u'alarmplan', u'evalAlarmplan')
    sections[u'Meldebild'] = (u'key', u'evalKey')
    sections[u'Hinweis'] = (u'remark', u'')
    sections[u'Funkkan\xe4le'] = (u'remark2', u'')
    sections[u'Geforderte Einsatzmittel bzw. Ausr\xfcstung'] = (u'material', u'evalMaterial')
    sections[u'(Alarmschreiben Ende)'] = (u'', u'')
    keywords = [u'Alarmschreiben', u'Feuerwehreinsatzzentrale']
    translations = AlarmFaxChecker.translations + [u'_bab_', u'_train_', u'_street_', u'_default_city_', u'_interchange_', u'_kilometer_', u'_train_identifier_']

    def getEvalMethods(self):
        """get all eval methods of fax checker

        :return: list of names of eval methods
        """
        return [m for m in self.__class__.__dict__.keys() if m.startswith('eval')]

    # eval methods for fax text recognition
    @staticmethod
    def evalStreet(fieldname, **params):
        alarmtype = None
        options = []
        if 'alarmtype' in params:
            alarmtype = params['alarmtype']
        if 'options' in params:
            options = params['options']

        streets = Street.getStreets()
        _str = FezAlarmFaxChecker().fields[fieldname][0]
        if 'part' in options:  # addresspart, remove city names
            for c in City.getCities():
                if _str.endswith(c.name):
                    _str = _str.replace(c.name, '')
            pattern = re.compile(r'(?P<street>(^(\D+))) (?P<housenumber>(?P<hn>([0-9]{1,3}((\s?)[a-z])?)).*)'  # street with housenumber
                                 r'|((?P<streetname>(^(\D+))))'
                                 r'|((?P<bab>((.*) (\>) )(?P<direction>(.*))))'  # highway
                                 r'|((.*) (?P<train>(KM .*).*))')  # train
        else:
            pattern = re.compile(r'(?P<street>(^(\D+))) (?P<housenumber>(?P<hn>([0-9]{1,3}((\s?)[a-z])?)).*)'  # street with housenumber
                                 r'|((?P<bab>A[0-9]{2,3} [A-Za-z]+) (?P<direction>(\D*))(( (?P<as>[0-9]*))|(.*)))'  # highway
                                 r'|((.*)(?P<train>(Bahnstrecke .*)) (?P<km>[0-9]+(.*)))'  # train
                                 r'|((?P<streetname>(^(\D+))))'
                                 )

        m = pattern.match(_str)
        if m:
            if m.groupdict()['street'] or m.groupdict()['streetname']:  # normal street, fields: 'street', 'housenumber' with sub 'hn'
                repl = difflib.get_close_matches(m.groupdict()['street'] or m.groupdict()['streetname'], [s.name for s in streets], 1)
                if len(repl) > 0:
                    _streets = [s for s in filter(lambda s: s.name == repl[0], streets)]
                    if len(_streets) > 0:
                        if FezAlarmFaxChecker().fields['city'][1] != 0:  # city given
                            for _s in _streets:  # find correct city
                                if _s.city.id == FezAlarmFaxChecker().fields['city'][1]:
                                    _street = _s
                                    _streets = [_s]
                                    break
                            FezAlarmFaxChecker().fields[fieldname] = (_street.name, _street.id)
                            FezAlarmFaxChecker().logger.debug(u'street: "{}" ({}) found'.format(_street.name, _street.id))
                        else:
                            FezAlarmFaxChecker().fields[fieldname] = (m.groupdict()['street'] or m.groupdict()['streetname'], 0)
                            if not re.match(alarmtype.translation(u'_street_'), _str[1]) and 'part' not in options:  # ignore 'street' value and part-address
                                FezAlarmFaxChecker().fields['streetno'] = (m.groupdict()['housenumber'], 0)

                    if m.groupdict()['hn'] and FezAlarmFaxChecker().fields['city'][1] != 0:
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
                                FezAlarmFaxChecker().fields['id.streetno'] = (db_hn[0].number, db_hn[0].id)
                                FezAlarmFaxChecker().fields['streetno'] = (_housenumber, db_hn[0].id)
                                FezAlarmFaxChecker().fields['lat'] = (db_hn[0].points[0][0], db_hn[0].id)
                                FezAlarmFaxChecker().fields['lng'] = (db_hn[0].points[0][1], db_hn[0].id)
                            elif _housenumber:
                                FezAlarmFaxChecker().fields['streetno'] = (_housenumber, 0)
                                FezAlarmFaxChecker().fields['lat'] = (_streets[0].lat, 0)
                                FezAlarmFaxChecker().fields['lng'] = (_streets[0].lng, 0)
                            else:
                                FezAlarmFaxChecker().fields['lat'] = (_streets[0].lat, 0)
                                FezAlarmFaxChecker().fields['lng'] = (_streets[0].lng, 0)

            elif m.groupdict()['bab']:  # highway, fields: 'bab', 'direction', 'as'
                repl = difflib.get_close_matches(u"{} {}".format(m.groupdict()['bab'], m.groupdict()['direction']), [s.name for s in streets], 1)
                if len(repl) > 0:
                    _streets = [s for s in filter(lambda s: s.name == repl[0], streets)]
                    if len(_streets) > 0:
                        _street = _streets[0]
                        FezAlarmFaxChecker().fields[fieldname] = (_street.name, _street.id)
                        FezAlarmFaxChecker().logger.debug(u'street: "{}" ({}) found'.format(_street.name, _street.id))
                return

            elif m.groupdict()['train']:  # train, fields: 'train', 'km'
                repl = difflib.get_close_matches(m.groupdict()['train'], [s.name for s in streets], 1)
                if len(repl) > 0:
                    _streets = [s for s in filter(lambda s: s.name == repl[0], streets)]
                    if len(_streets) > 0:
                        _street = _streets[0]
                        FezAlarmFaxChecker().fields[fieldname] = (_street.name, _street.id)
                        FezAlarmFaxChecker().logger.debug(u'street: "{}" ({}) found'.format(_street.name, _street.id))

                return

            else:  # not found
                repl = difflib.get_close_matches(_str, [s.name for s in streets])
                if len(repl) >= 1:
                    try:
                        street_id = u';'.join([u'{}'.format(s.id) for s in filter(lambda s: s.name == repl[0], streets)])
                    except:
                        street_id = u''

                    FezAlarmFaxChecker().fields[fieldname] = (u'{}'.format(repl[0]), street_id)
                    if 'streetno' not in FezAlarmFaxChecker().fields or FezAlarmFaxChecker().fields['streetno'] == u"":
                        FezAlarmFaxChecker().fields['streetno'] = (u'{}'.format(u" ".join(_str[repl[0].count(u' ') + 1:])).replace(alarmtype.translation(u'_street_'), u'').strip(), street_id)
                return
        else:
            FezAlarmFaxChecker().fields[fieldname] = (_str, 0)
            return

    @staticmethod
    def evalMaterial(fieldname, **params):
        cars = Car.getCars(params=['onlyactive'])
        carlist = [u'{} {}'.format(c.dept.name, c.name) for c in cars]
        c = [[], []]

        departements = Department.getDepartments()
        for p in [l for l in re.split(r"[\s]{2,}|[\n]+", FezAlarmFaxChecker().fields[fieldname][0])]:
            addcar = None
            if len([d for d in departements if d.name == p.strip()]) == 1:  # department default found
                c = [[u'default'], [0]]
                FezAlarmFaxChecker().logger.debug(u'material: "{}" default department found'.format(p.strip()))
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
            FezAlarmFaxChecker().logger.debug(u'material: done with {}, {}'.format(c[0], c[1]))
            FezAlarmFaxChecker().fields[fieldname] = (u','.join(c[0]), u','.join([str(_c) for _c in c[1]]))

    @staticmethod
    def evalTime(fieldname, **params):
        _str = FezAlarmFaxChecker().fields[fieldname][0]
        for r in [u'D', u'U']:
            _str = _str.replace(r, u'0')
        _str = _str.split()
        d = t = ''
        try:
            d = _str[4]
            t = _str[5]
            if len(re.findall(r"\d{2}.\d{2}.\d{4}", d)) == 1 and len(re.findall(r"\d{2}:\d{2}", t)) == 1:
                FezAlarmFaxChecker().fields[fieldname] = (u'{} - {}:00'.format(d, t), 1)
                FezAlarmFaxChecker().logger.debug(u'time: done with {} - {}:00'.format(d, t))
            else:
                d = d.replace(u'B', u'6')
                t = t.replace(u'B', u'6')
                if len(re.findall(r"\d{2}.\d{2}.\d{4}", d)) == 1 and len(re.findall(r"\d{2}:\d{2}", t)) == 1:
                    FezAlarmFaxChecker().fields[fieldname] = (u'{} - {}:00'.format(d, t), 1)
                    FezAlarmFaxChecker().logger.debug(u'time: done with {} - {}:00'.format(d, t))
        except:
            import traceback
            FezAlarmFaxChecker().fields[fieldname] = (u'{} - {}:00'.format(d, t), 0)
            FezAlarmFaxChecker().logger.error(u'time: error done with {} - {}:00\n{}'.format(d, t, traceback.format_exc()))
        return

    @staticmethod
    def evalObject(fieldname, **params):
        _str = FezAlarmFaxChecker().fields[fieldname][0].replace('\xc3\x9c'.decode('utf-8'), u'0')
        objects = AlarmObject.getAlarmObjects()
        repl = difflib.get_close_matches(_str, [o.name for o in objects], 1)
        if repl:
            o = filter(lambda o: o.name == repl[0], objects)
            FezAlarmFaxChecker().fields[fieldname] = (repl[0], o[0].id)
            FezAlarmFaxChecker().logger.debug(u'object: "{}" objectlist -> {}'.format(_str, repl[0]))
        else:
            s = ""
            for p in _str.split():
                s += p
                repl = difflib.get_close_matches(s, [o.name for o in objects], 1)

                if len(repl) == 1:
                    o = filter(lambda o: o.name == repl[0], objects)
                    FezAlarmFaxChecker().fields[fieldname] = (repl[0], o[0].id)
                    FezAlarmFaxChecker().logger.debug(u'object: "{}" special handling -> {}'.format(_str, repl[0]))
                    return

            FezAlarmFaxChecker().fields[fieldname] = (_str, 0)
        return

    @staticmethod
    def evalAlarmplan(fieldname, **params):
        _str = FezAlarmFaxChecker().fields[fieldname][0].replace(u'B', u'6').strip()
        FezAlarmFaxChecker().fields[fieldname] = (_str, 1)
        return

    @staticmethod
    def evalKey(fieldname, **params):
        if fieldname in FezAlarmFaxChecker().fields:
            _str = FezAlarmFaxChecker().fields[fieldname][0]
        else:  # key not found
            FezAlarmFaxChecker().fields[fieldname] = (u'----', 0)
            raise
        if _str == '':
            FezAlarmFaxChecker().fields[fieldname] = (_str, 0)
            return
        keys = {}
        try:
            for k in Alarmkey.getAlarmkeys():
                keys[k.key] = k.id

            repl = difflib.get_close_matches(_str.strip(), keys.keys(), 1, cutoff=0.8)  # default cutoff 0.6
            if len(repl) == 0:
                repl = difflib.get_close_matches(_str.strip(), keys.keys(), 1)  # try with default cutoff
            if len(repl) > 0:
                k = Alarmkey.getAlarmkeys(int(keys[repl[0]]))
                FezAlarmFaxChecker().fields[fieldname] = (u'{}: {}'.format(k.category, k.key), k.id)
                FezAlarmFaxChecker().logger.debug(u'key: found "{}: {}"'.format(k.category, k.key))
                return
            FezAlarmFaxChecker().logger.info(u'key: "{}" not found in alarmkeys'.format(_str))
            FezAlarmFaxChecker().fields[fieldname] = (_str, 0)
        except:
            FezAlarmFaxChecker().logger.error(u'key: error in key evaluation')
        finally:
            return

    @staticmethod
    def evalCity(fieldname, **params):
        if fieldname in FezAlarmFaxChecker().fields:
            _str = FezAlarmFaxChecker().fields[fieldname][0]
        else:  # city not found -> use default city
            city = City.getDefaultCity()
            FezAlarmFaxChecker().fields[fieldname] = (city.name, city.id)
            raise

        alarmtype = None
        if 'alarmtype' in params:
            alarmtype = params['alarmtype']

        if _str.strip() == '':
            FezAlarmFaxChecker().fields[fieldname] = ('', 0)

        cities = City.getCities()
        for city in cities:  # test first word with defined subcities of cities
            try:
                repl = difflib.get_close_matches(_str.split()[0], city.subcities + [city.name], 1, cutoff=0.7)
                if len(repl) > 0:
                    FezAlarmFaxChecker().fields[fieldname] = (repl[0], city.id)
                    return
            except:
                pass

        for city in cities:  # test whole string with subcities
            repl = difflib.get_close_matches(_str, city.subcities + [city.name], 1)
            if len(repl) > 0:
                FezAlarmFaxChecker().fields[fieldname] = (repl[0], city.id)
                return

        for s in _str.split():
            for c in cities:
                repl = difflib.get_close_matches(s, [c.name], 1, cutoff=0.7)
                if len(repl) == 1:
                    FezAlarmFaxChecker().fields[fieldname] = (repl[0], c.id)
                    return

        if alarmtype.translation(u'_default_city_') in _str.lower():
            d_city = filter(lambda c: c.default == 1, cities)
            if len(d_city) == 1:
                FezAlarmFaxChecker().fields[fieldname] = (d_city[0].name, d_city[0].id)
                return

            # use default city
            city = City.getDefaultCity()
            FezAlarmFaxChecker().fields[fieldname] = (city.name, city.id)
            return

        if _str.startswith('in'):  # remove 'in' and plz
            _str = re.sub(r'in*|[0-9]*', '', _str[2:].strip())

        FezAlarmFaxChecker().fields[fieldname] = (_str, 0)  # return original if no match
        return

    @staticmethod
    def evalAddressPart(fieldname, options="", **params):
        alarmtype = None
        options = []
        if 'alarmtype' in params:
            alarmtype = params['alarmtype']
        if 'options' in params:
            options = params['options']
        _str = FezAlarmFaxChecker().fields[fieldname][0].strip().replace(u'\r', u'').replace(u'\n', u'')
        FezAlarmFaxChecker().fields[fieldname] = (_str, 0)
        options.append('part')
        params['options'] = filter(None, options)
        FezAlarmFaxChecker().evalStreet(fieldname, **params)

        if _str.endswith(')') and alarmtype.translation(u'_interchange_') in _str:  # bab part found
            part = '{}'.format(_str[_str.rfind('(') + 1:-1].replace(u'\n', u' '))
            FezAlarmFaxChecker().fields[fieldname] = (u'{}: {}'.format(alarmtype.translation(u'_kilometer_'), part), -1)
            if FezAlarmFaxChecker().fields['address'][1] != 0:
                _streets = Street.getStreets(id=FezAlarmFaxChecker().fields['address'][1])
                numbers = _streets.housenumbers
                hn = difflib.get_close_matches(part, [n.number for n in numbers], 1)
                FezAlarmFaxChecker().fields['zoom'] = (u'14', 1)
                if len(hn) == 1:
                    nr = [n for n in numbers if n.number == hn[0]][0]
                    FezAlarmFaxChecker().fields['streetno'] = (nr.number, nr.id)
                    FezAlarmFaxChecker().fields['id.streetno'] = (nr.id, nr.id)
                    FezAlarmFaxChecker().fields['lat'] = (nr.points[0][0], nr.id)
                    FezAlarmFaxChecker().fields['lng'] = (nr.points[0][1], nr.id)
                return

        elif alarmtype.translation(u'_train_identifier_') in _str:  # found train position
            part = u'{}'.format(_str[_str.find(alarmtype.translation(u'_train_identifier_')):])
            FezAlarmFaxChecker().fields[fieldname] = (u'{}'.format(part), 1)
            numbers = Street.getStreets(id=FezAlarmFaxChecker().fields['address'][1]).housenumbers

            for nr in numbers:
                if part.startswith(nr.number):
                    FezAlarmFaxChecker().fields['streetno'] = (nr.number, nr.id)
                    FezAlarmFaxChecker().fields['id.streetno'] = (nr.id, nr.id)
                    FezAlarmFaxChecker().fields['lat'] = (nr.points[0][0], nr.id)
                    FezAlarmFaxChecker().fields['lng'] = (nr.points[0][1], nr.id)
                    FezAlarmFaxChecker().fields['zoom'] = (u'15', 1)
                    return

        else:
            if FezAlarmFaxChecker().fields[fieldname][1] != 0:
                return
            part = _str

        FezAlarmFaxChecker().fields[fieldname] = (part, -1)
        return

    def buildAlarmFromText(self, alarmtype, rawtext):
        values = {}

        if alarmtype:
            sections = alarmtype.getSections()
            sectionnames = dict(zip([s.name for s in sections], [s.key for s in sections]))
            sectionmethods = dict(zip([s.key for s in sections], [s.method for s in sections]))
            FezAlarmFaxChecker().fields['alarmtype'] = (alarmtype, 0)
        else:  # matching alarmtype found
            return values

        curr_field = ""

        #for l in rawtext.decode('utf-8').split(u"\n"):
        for l in rawtext.split(u"\n"):
            field = difflib.get_close_matches(re.split(u':|=|i ', l)[0], sectionnames.keys(), 1)  # test line ->:|=
            if len(field) == 0 and u" " in l:
                field = difflib.get_close_matches(l.split()[0], sectionnames.keys(), 1)  # test line first word

            if len(field) == 1:
                value = u":".join(re.split(u':|=|i ', l)[1:]).strip()
            else:
                field = []  # field has to be empty -> prevent overwriting
                value = l
            if len(field) == 1:
                if sectionnames[field[0]] != u'':
                    FezAlarmFaxChecker().fields[sectionnames[field[0]]] = (value, 0)

                curr_field = field[0]
            elif curr_field != '':
                if sectionnames[curr_field] != u'':
                    #FezAlarmFaxChecker().fields[sectionnames[curr_field]] = (FezAlarmFaxChecker().fields[sectionnames[curr_field]][0] + u'\n' + value, FezAlarmFaxChecker().fields[sectionnames[curr_field]][1])
                    if value[0] == u' ':
                        FezAlarmFaxChecker().fields[sectionnames[curr_field]] = (u"\n".join((FezAlarmFaxChecker().fields[sectionnames[curr_field]][0], value)), FezAlarmFaxChecker().fields[sectionnames[curr_field]][1])
                    else:
                        FezAlarmFaxChecker().fields[sectionnames[curr_field]] = (u"".join((FezAlarmFaxChecker().fields[sectionnames[curr_field]][0], value)), FezAlarmFaxChecker().fields[sectionnames[curr_field]][1])

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
                    getattr(self, method)(k, alarmtype=alarmtype, options=method_params.split(';'))  # fieldname, parameters
                except:
                    if u'error' not in values:
                        values['error'] = ''
                    values['error'] = u"".join((values['error'], u'error in method: {}\n'.format(method)))
                    import traceback
                    FezAlarmFaxChecker().logger.error(u'error in section {} {}\n{}'.format(k, method, traceback.format_exc()))

        for k in FezAlarmFaxChecker().fields:
            try:
                values[k] = (FezAlarmFaxChecker().fields[k][0].decode('utf-8'), FezAlarmFaxChecker().fields[k][1])
            except:
                values[k] = (FezAlarmFaxChecker().fields[k][0], FezAlarmFaxChecker().fields[k][1])
        return values
