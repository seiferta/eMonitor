from flask import request
from emonitor.modules.settings.settings import Settings
from emonitor.modules.streets.street import Street
from emonitor.modules.streets.city import City
from emonitor.modules.alarms.alarm import Alarm
from emonitor.modules.maps.map import Map


def getFrontendData(self):
    """
    Deliver frontend content of module streets (ajax)

    :return: rendered template as string or json dict
    """
    if request.args.get('action') == 'streetcoords':  # get map parameter for given streetid

        if request.args.get('id') not in ['', 'None']:
            street = Street.getStreets(id=request.args.get('id'))
            return {'lat': street.lat, 'lng': street.lng, 'zoom': street.zoom, 'way': street.navigation,
                    'cityid': street.cityid, 'cityname': street.city.name}

    elif request.args.get('action') == 'housecoords':  # deliver center of housenumbers
        if request.args.get('streetid') != '' and request.args.get('housenumber') != '':
            street = Street.getStreet(id=request.args.get('streetid'))
            hnumber = street.getHouseNumber(number=request.args.get('housenumber').split()[0])
            if hnumber:
                return hnumber.getPosition(0)

            return {'lat': street.lat, 'lng': street.lng}
        return {}

    elif request.args.get('action') == 'defaultposition':

        return {'defaultlat': float(Settings.get('defaultLat')),
                'defaultlng': float(Settings.get('defaultLng')),
                'defaultzoom': int(Settings.get('defaultZoom'))}

    elif request.args.get('action') == 'alarmposition':
        alarm = Alarm.getAlarms(id=request.args.get('alarmid'))
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
        for c in City.getCities():
            cities[c.id] = c.name
            for k, street in c.streets.iteritems():
                if street.active:
                    try:
                        streets[str(street.id)] = '%s (%s)' % (street.name, c.name)
                    except:
                        streets[str(street.id)] = '%s (-%s-)' % (street.name, street.cityid)
        return streets

    elif request.args.get('action') == 'defaultmap':
        dmap = Map.getDefaultMap()
        return {'tileserver': dmap.tileserver, 'name': dmap.name}

    return ""
