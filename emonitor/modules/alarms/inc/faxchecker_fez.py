from collections import OrderedDict
import re
import difflib
from emonitor.modules.alarms.alarmutils import AlarmFaxChecker
from emonitor.extensions import classes

__all__ = ['FezAlarmFaxChecker']


class FezAlarmFaxChecker(AlarmFaxChecker):
    __name__ = "FEZ"
    __version__ = '0.1'

    fields = {}

    def getEvalMethods(self):
        return [m for m in self.__class__.__dict__.keys() if m.startswith('eval')]

    def getDefaultConfig(self):
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
        sections[u'Geforderte Einsatzmittel bzw. Ausr\xfcstung'] = (u'', u'')
        sections[u'(Alarmschreiben Ende)'] = (u'', u'')
        translations = [u'_bab_', u'_train_', u'_street_', u'_default_city_', u'_interchange_', u'_kilometer_', u'_bma_', u'_bma_main_', u'_bma_key_', u'_train_identifier_']
        return {u'keywords': [u'Alarmschreiben', u'Feuerwehreinsatzzentrale'], u'sections': sections, u'translations': translations}  # section: ('key', 'method')

    # eval methods for fax text recognition
    @staticmethod
    def evalStreet(fieldname, **params):
        alarmtype = None
        options = []
        if 'alarmtype' in params:
            alarmtype = params['alarmtype']
        if 'options' in params:
            options = params['options']

        streets = classes.get('street').getAllStreets()
        _str = FezAlarmFaxChecker().fields[fieldname][0]
        if 'part' in options:  # addresspart, remove city names
            for c in classes.get('city').getCities():
                if _str.endswith(c.name.encode('utf-8')):
                    _str = _str.replace(c.name.encode('utf-8'), '')

        # try special handling for bab and bahn
        repl = difflib.get_close_matches(_str, [s.name.encode('utf-8') for s in streets], 1)
        if len(repl) == 1:  # found street
            _streets = [s for s in filter(lambda s: s.name.encode('utf-8') == repl[0], streets)]
            if len(_streets) > 0:
                _street = _streets[0]
                FezAlarmFaxChecker().fields[fieldname] = ('%s' % _street.name, _street.id)
                if unicode(_street.subcity) in [alarmtype.translation(u'_bab_'), alarmtype.translation(u'_train_')]:  # only bab and train type
                    return

        _str = _str.split()

        if FezAlarmFaxChecker().fields['city'][1] != 0:  # city found
            if len(_str) >= 2:  # streetname + no
                fstreets = filter(lambda s: s.city.id == FezAlarmFaxChecker().fields['city'][1], streets)

                # try streets with space in name
                i = 1
                while i < len(_str):
                    repl = difflib.get_close_matches(' '.join(_str[0:i]), [s.name.encode('utf-8') for s in fstreets], 1)
                    if len(repl) > 0:
                        if i == 1:
                            i += repl[0].count(' ')
                        break
                    i += 1

                if len(repl) >= 1:  # found in db + houseno.
                    _streets = [s for s in filter(lambda s: s.name.encode('utf-8') == repl[0], fstreets)]
                    FezAlarmFaxChecker().fields[fieldname] = ('%s' % repl[0], ';'.join('%s' % s.id for s in _streets))
                    try:
                        _str[i] = _str[i].replace('B', '6').replace('\xc3\x9c', '0')
                        _str[i] = ' '.join(_str[i:])
                    except IndexError:
                        i = len(_str) - 1
                        _str[i] = ''
                    if 'part' not in options:
                        FezAlarmFaxChecker().fields['streetno'] = ('%s' % _str[i].replace(alarmtype.translation(u'_street_').encode('utf-8'), '').strip(), FezAlarmFaxChecker().fields[fieldname][1])

                    if len(_streets) == 1 and 'part' not in options:  # housenumber of street
                        _hn = None
                        if len(FezAlarmFaxChecker().fields['streetno'][0].split()) > 0:
                            _hn = FezAlarmFaxChecker().fields['streetno'][0].split()[0].replace('O', '0')

                        for hnumber in _streets[0].housenumbers:
                            if _hn and str(hnumber.number) == _hn:
                                FezAlarmFaxChecker().fields['id.streetno'] = (hnumber.number, hnumber.id)
                                nr = hnumber.number
                                if FezAlarmFaxChecker().fields['streetno'][0].split() > 1:
                                    nr += ' ' + ' '.join(FezAlarmFaxChecker().fields['streetno'][0].split()[1:]).replace('.0G', '. OG')
                                FezAlarmFaxChecker().fields['streetno'] = (nr, hnumber.id)
                                FezAlarmFaxChecker().fields['lat'] = (hnumber.points[0][0], hnumber.id)
                                FezAlarmFaxChecker().fields['lng'] = (hnumber.points[0][1], hnumber.id)
                                break

                        if 'id.streetno' not in FezAlarmFaxChecker().fields:  # spaces in house number
                            _hn = FezAlarmFaxChecker().fields['streetno'][0].replace(' ', '')
                            for hnumber in _streets[0].housenumbers:
                                if _hn and str(hnumber.number) == _hn:
                                    FezAlarmFaxChecker().fields['id.streetno'] = (hnumber.number, hnumber.id)
                                    FezAlarmFaxChecker().fields['streetno'] = (hnumber.number, hnumber.id)
                                    FezAlarmFaxChecker().fields['lat'] = (hnumber.points[0][0], hnumber.id)
                                    FezAlarmFaxChecker().fields['lng'] = (hnumber.points[0][1], hnumber.id)
                                    break

                else:  # street not found
                    if fieldname not in FezAlarmFaxChecker().fields:
                        FezAlarmFaxChecker().fields[fieldname] = (" ".join(_str), 0)
                return

            else:
                repl = difflib.get_close_matches(" ".join(_str), [s.name.encode('utf-8') for s in streets])
                if len(repl) >= 1:
                    try:
                        street_id = ';'.join(['%s' % s.id for s in filter(lambda s: s.name.encode('utf-8') == repl[0], streets)])
                    except:
                        street_id = ''

                    FezAlarmFaxChecker().fields[fieldname] = ('%s' % repl[0], street_id)
                    if not 'streetno' in FezAlarmFaxChecker().fields or FezAlarmFaxChecker().fields['streetno'] == "":
                        FezAlarmFaxChecker().fields['streetno'] = ('%s' % " ".join(_str[repl[0].count(" ") + 1:]).replace('Stra\xc3\x9fe', '').strip(), street_id)
                return

        else:  # other city
            if len(_str) == 2:  # streetname + no
                FezAlarmFaxChecker().fields[fieldname] = ('%s' % _str[0], 0)
                FezAlarmFaxChecker().fields['streetno'] = (_str[1], 0)
            else:
                FezAlarmFaxChecker().fields[fieldname] = (" ".join(_str), 0)
            return

    @staticmethod
    def evalMaterial(fieldname, **params):
        cars = classes.get('car').getCars(params=['onlyactive'])
        carlist = ['%s %s' % (c.dept.name, c.name) for c in cars]
        carids = [('%s' % c.id) for c in cars]
        c = []
        cl = []

        departements = classes.get('department').getDepartments()
        for p in re.split("\s\s|\\\\n", FezAlarmFaxChecker().fields[fieldname][0]):
            if len([d for d in departements if d.name == p.strip()]) == 1:  # department default found
                c.append('default')
                cl.append('0')
                continue

            repl = difflib.get_close_matches(p.strip(), carlist, 1)
            if len(repl) == 1:
                _id = carids[carlist.index(repl[0])]
                if _id not in cl:  # prevent double
                    c.append(repl[0])
                    cl.append(_id)

            else:  # try car descriptions
                descriptionlist = ['%s %s' % (cn.dept.name, cn.description) for cn in cars]
                repl = difflib.get_close_matches(p.strip(), descriptionlist, 1)
                if len(repl) == 1:
                    _id = carids[descriptionlist.index(repl[0])]
                    if _id not in cl:  # prevent double
                        c.append(repl[0])
                        cl.append(_id)

                else:
                    t = ""
                    for x in p.split():
                        t += x
                        repl = difflib.get_close_matches(t, carlist, 1)
                        if len(repl) == 1:
                            _id = carids[carlist.index(repl[0])]
                            if _id not in cl:  # prevent double
                                c.append(repl[0])
                                cl.append(_id)
                            break

        if len(c) > 0:
            FezAlarmFaxChecker().fields[fieldname] = (','.join(c), ','.join(cl))

    @staticmethod
    def evalTime(fieldname, **params):
        _str = FezAlarmFaxChecker().fields[fieldname][0]
        for r in ['D', 'U', '\xc3\x9c']:
            _str = _str.replace(r, '0')
        _str = _str.split()
        d = t = ''
        try:
            d = _str[4]
            t = _str[5]
            if len(re.findall("\d{2}.\d{2}.\d{4}", d)) == 1 and len(re.findall("\d{2}:\d{2}", t)) == 1:
                FezAlarmFaxChecker().fields[fieldname] = ('%s - %s:00' % (d, t), 1)
            else:
                d = d.replace('B', '6')
                t = t.replace('B', '6')
                if len(re.findall("\d{2}.\d{2}.\d{4}", d)) == 1 and len(re.findall("\d{2}:\d{2}", t)) == 1:
                    FezAlarmFaxChecker().fields[fieldname] = ('%s - %s:00' % (d, t), 1)
        except:
            FezAlarmFaxChecker().fields[fieldname] = ('%s - %s:00' % (d, t), 0)
        return

    @staticmethod
    def evalObject(fieldname, **params):
        _str = FezAlarmFaxChecker().fields[fieldname][0].replace('\xc3\x9c', '0')
        objects = classes.get('alarmobject').getAlarmObjects()
        repl = difflib.get_close_matches(_str, [o.name.encode('utf-8') for o in objects], 1)
        if repl:
            o = filter(lambda o: o.name.encode('utf-8') == repl[0], objects)
            FezAlarmFaxChecker().fields[fieldname] = (repl[0], o[0].id)

        else:
            s = ""
            for p in _str.split():
                s += p
                repl = difflib.get_close_matches(s, [o.name.encode('utf-8') for o in objects], 1)

                if len(repl) == 1:
                    o = filter(lambda o: o.name.encode('utf-8') == repl[0], objects)
                    FezAlarmFaxChecker().fields[fieldname] = (repl[0], o[0].id)
                    return

            FezAlarmFaxChecker().fields[fieldname] = (_str, 0)
        return

    @staticmethod
    def evalAlarmplan(fieldname, **params):
        _str = FezAlarmFaxChecker().fields[fieldname][0].replace('B', '6').strip()
        FezAlarmFaxChecker().fields[fieldname] = (_str, 1)
        return

    @staticmethod
    def evalKey(fieldname, **params):
        _str = FezAlarmFaxChecker().fields[fieldname][0]

        keys = {}
        try:
            for k in classes.get('alarmkey').getAlarmkeys():
                keys[k.key] = k.id

            repl = difflib.get_close_matches(_str.strip(), keys.keys(), 1)
            if len(repl) > 0:
                k = classes.get('alarmkey').getAlarmkeys(int(keys[repl[0]]))
                FezAlarmFaxChecker().fields[fieldname] = ('%s: %s' % (k.category, k.key), k.id)
                return
            FezAlarmFaxChecker().fields[fieldname] = (_str, 0)
        except:
            pass
        finally:
            return

    @staticmethod
    def evalCity(fieldname, **params):
        _str = FezAlarmFaxChecker().fields[fieldname][0]
        alarmtype = None
        if 'alarmtype' in params:
            alarmtype = params['alarmtype']

        if _str.strip() == '':
            FezAlarmFaxChecker().fields[fieldname] = ('', 0)

        cities = classes.get('city').getCities()
        for city in cities:  # test first word with defined subcities of cities
            try:
                repl = difflib.get_close_matches(_str.split()[0], city.getSubCityList() + [city.name], 1)
                if len(repl) > 0:
                    FezAlarmFaxChecker().fields[fieldname] = (repl[0], city.id)
                    return
            except:
                pass

        for city in cities:  # test whole string with subcities
            repl = difflib.get_close_matches(_str, city.getSubCityList() + [city.name], 1)
            if len(repl) > 0:
                FezAlarmFaxChecker().fields[fieldname] = (repl[0], city.id)
                return

        for s in _str.split():
            for c in cities:
                repl = difflib.get_close_matches(s, [c.name], 1)
                if len(repl) == 1:
                    FezAlarmFaxChecker().fields[fieldname] = (repl[0], c.id)
                    return

        if alarmtype.translation(u'_default_city_') in _str.lower():
            d_city = filter(lambda c: c.default == 1, cities)
            if len(d_city) == 1:
                FezAlarmFaxChecker().fields[fieldname] = (d_city[0].name, d_city[0].id)
                return

            # use default city
            city = classes.get('city').getDefaultCity()
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
        _str = FezAlarmFaxChecker().fields[fieldname][0].strip().replace('\r', '').replace('\n', '')
        options.append('part')
        params['options'] = filter(None, options)
        FezAlarmFaxChecker().evalStreet(fieldname, **params)
        try:
            _str = unicode(_str)
        except:
            pass
        if _str.endswith(')') and alarmtype.translation(u'_interchange_') in _str:  # bab part found
            part = '%s' % _str[_str.rfind('(') + 1:-1].replace('\n', ' ')
            FezAlarmFaxChecker().fields[fieldname] = ('%s: %s' % (alarmtype.translation(u'_kilometer_'), part), 1)
            numbers = classes.get('street').getStreet(FezAlarmFaxChecker().fields['address'][1]).housenumbers
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
            part = '%s' % _str[_str.find(alarmtype.translation(u'_train_identifier_')):]
            FezAlarmFaxChecker().fields[fieldname] = ('%s' % part, 1)
            numbers = classes.get('street').getStreet(FezAlarmFaxChecker().fields['address'][1]).housenumbers

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
            sectionnames = dict(zip([s.name.encode('utf-8') for s in sections], [s.key for s in sections]))
            sectionmethods = dict(zip([s.key for s in sections], [s.method for s in sections]))
            FezAlarmFaxChecker().fields['alarmtype'] = (alarmtype, 0)
        else:  # matching alarmtype found
            return values

        curr_field = ""

        for l in rawtext.split("\n"):
            field = difflib.get_close_matches(l.split(': ')[0], sectionnames.keys(), 1)  # test line ->:
            if len(field) == 0 and " " in l:
                field = difflib.get_close_matches(l.split()[0], sectionnames.keys(), 1)  # test line first word

            if len(field) == 1 and l.startswith(field[0] + ': '):
                value = ":".join(l.split(':')[1:]).strip()
                if value.strip() == '':
                    value = ":".join(l.split('=')[1:]).strip()
            else:
                field = []  # field has to be empty -> prevent overwriting
                value = l

            if len(field) == 1:
                if sectionnames[field[0]] != '':
                    FezAlarmFaxChecker().fields[sectionnames[field[0]]] = (value, 0)

                curr_field = field[0]
            elif curr_field != '':
                if sectionnames[curr_field] != '':
                    FezAlarmFaxChecker().fields[sectionnames[curr_field]] = (FezAlarmFaxChecker().fields[sectionnames[curr_field]][0] + '\n' + value, FezAlarmFaxChecker().fields[sectionnames[curr_field]][1])

        for section in sections:  # sections in order
            k = section.key
            if sectionmethods[k] != "":
                method = sectionmethods[k].split(';')[0]
                try:  # method parameters (optional)
                    method_params = sectionmethods[k].split(';')[1]
                except:
                    method_params = ''

                # execute methods
                try:
                    getattr(self, method)(k, alarmtype=alarmtype, options=method_params.split(';'))  # fieldname, parameters
                except:
                    if u'error' not in values:
                        values['error'] = ''
                    values['error'] += 'error in method: %s\n' % method
                    pass

        for k in FezAlarmFaxChecker().fields:
            try:
                values[k] = (FezAlarmFaxChecker().fields[k][0].decode('utf-8'), FezAlarmFaxChecker().fields[k][1])
            except:
                values[k] = (FezAlarmFaxChecker().fields[k][0], FezAlarmFaxChecker().fields[k][1])
        return values
