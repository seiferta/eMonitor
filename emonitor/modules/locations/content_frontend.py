from collections import OrderedDict
from flask import render_template, request
from emonitor.extensions import classes, cache


@cache.memoize(5000)
def getFrontendContent(**params):

    if 'area' not in params.keys() and request.args.get('area', '') != '':
        params['area'] = request.args.get('area')

    if 'area' in params.keys() and params['area'] in ['west', 'east']:  # small area view
        streets = {}
        cities = classes.get('city').getCities()
        for c in cities:
            streets[c.id] = OrderedDict()
            for s in [st for st in c.getStreets() if st.active == 1]:
                if s.name[0] not in streets[c.id]:
                    streets[c.id][s.name[0]] = []
                streets[c.id][s.name[0]].append(s)
            streets[c.id] = sorted(streets[c.id].items(), key=lambda t: t[0])
        return render_template('frontend.locations_smallarea.html', cities=cities, streets=streets, alarmobjects=classes.get('alarmobject').getAlarmObjects(), alarmobjecttypes=classes.get('alarmobjecttype').getAlarmObjectTypes(), frontendarea=params['area'])

    return ""
    
    
def getFrontendData(self):

    if request.args.get('action') == 'locationslookup':  # load locations lookup
        locations = {}
        for street in classes.get('street').getAllStreets():  # load streets
            locations["s%s" %street.id] = '%s (%s)' % (street.name, street.city.name)
        for aobj in classes.get('alarmobject').getAlarmObjects():  # load alarmobjects
            locations["o%s" % aobj.id] = '%s <em>(%s)</em>' % (aobj.name, aobj.objecttype.name)
        return locations

    return ""
