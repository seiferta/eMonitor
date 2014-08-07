from collections import OrderedDict
from flask import render_template, request
from emonitor.extensions import classes, cache


@cache.cached(timeout=5000, key_prefix='frontend.locations')
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
        return render_template('frontend.locations_smallarea.html', cities=cities, streets=streets, alarmobjects=classes.get('alarmobject').getAlarmObjects(), frontendarea=params['area'])

    return "default"
    
    
def getFrontendData(self):
    return ""
