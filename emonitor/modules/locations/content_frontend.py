from flask import render_template, request
from emonitor.extensions import classes, cache


@cache.memoize(5000)
def getFrontendContent(**params):

    if 'area' not in params.keys() and request.args.get('area', '') != '':
        params['area'] = request.args.get('area')

    if 'area' in params.keys() and params['area'] in ['west', 'east']:  # small area view
        return render_template('frontend.locations_smallarea.html', cities=classes.get('city').getCities(), alarmobjects=classes.get('alarmobject').getAlarmObjects(), alarmobjecttypes=classes.get('alarmobjecttype').getAlarmObjectTypes(), frontendarea=params['area'])
    return ""


def getFrontendData(self):

    if request.args.get('action') == 'locationslookup':  # load locations lookup
        locations = {}
        for street in classes.get('street').getAllStreets():  # load streets
            locations["s%s" % street.id] = '%s (%s)' % (street.name, street.city.name)
        for aobj in classes.get('alarmobject').getAlarmObjects():  # load alarmobjects
            locations["o%s" % aobj.id] = '%s <em>(%s)</em>' % (aobj.name, aobj.objecttype.name)
        return locations

    if request.args.get('action') == 'streetsofcity':  # load all active streets of city
        streets = {}
        for s in classes.get('street').getAllStreets(cityid=int(request.args.get('cityid', '0'))):
            if s.name[0].upper() not in streets.keys():
                streets[s.name[0].upper()] = []
            streets[s.name[0].upper()].append(s)
        return render_template('frontend.locations_streets.html', streets=streets, cityid=int(request.args.get('cityid', '0')))

    return ""
