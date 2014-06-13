from flask import request
from emonitor.extensions import classes


def getFrontendData(self):
    if request.args.get('action') == 'streetcoords':  # get map parameter for given streetid

        if request.args.get('id') != '':
            street = classes.get('street').getStreet(request.args.get('id'))
            return {'lat': street.lat, 'lng': street.lng, 'zoom': street.zoom, 'way': street.navigation,
                    'cityid': street.cityid}

    elif request.args.get('action') == 'housecoords':  # deliver center of housenumbers
        if request.args.get('streetid') != '' and request.args.get('housenumber') != '':
            street = classes.get('street').getStreet(request.args.get('streetid'))
            hnumber = [h for h in street.housenumbers if h.number == request.args.get('housenumber').split()[0]]
            if len(hnumber) > 0:
                return {'lat': hnumber[0].points[0][0], 'lng': hnumber[0].points[0][1]}

            return {'lat': street.lat, 'lng': street.lng}
        return {}

    elif request.args.get('action') == 'defaultposition':

        return {'defaultlat': float(classes.get('settings').get('defaultLat')),
                'defaultlng': float(classes.get('settings').get('defaultLng')),
                'defaultzoom': int(classes.get('settings').get('defaultZoom'))}

    elif request.args.get('action') == 'alarmposition':
        alarm = classes.get('alarm').getAlarms(id=request.args.get('alarmid'))
        if alarm:
            return {'id': request.args.get('alarmid'), 'alarmlat': alarm.lat, 'alarmlng': alarm.lng,
                    'alarmzoom': alarm.zoom, 'marker': alarm.marker, 'alarmprio': alarm.priority,
                    'alarmstreet': alarm.street.name, 'alarmstreetno': alarm.get('streetno'),
                    'alarmstreet2': alarm.get('address2'), 'alarmcity': alarm.city.name,
                    'alarmsubcity': alarm.street.subcity}
        else:
            return {'id': '0'}

    elif request.args.get('action') == 'streetslookup':
        streets = {}
        cities = {}
        for c in classes.get('city').getCities():
            cities[c.id] = c.name
            for street in c.getStreets():
                if street.active:
                    try:
                        streets[str(street.id)] = '%s (%s)' % (street.name, c.name)
                    except:
                        streets[str(street.id)] = '%s (-%s-)' % (street.name, street.cityid)
        return streets

    elif request.args.get('action') == 'defaultmap':
        dmap = classes.get('map').getDefaultMap()
        return {'tileserver': dmap.tileserver, 'name': dmap.name}

    return ""