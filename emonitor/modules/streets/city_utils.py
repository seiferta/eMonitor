import requests
from xml.dom import minidom

from flask import current_app, render_template

from emonitor.modules.maps.map import Map
from emonitor.modules.streets.city import City

URL = 'http://overpass-api.de/api/interpreter'


def loadCitiesFromOsm():  # load all cities in bounding box
    global URL
    map_details = Map.getMaps()[0].getMapBox(tilepath=current_app.config.get('PATH_TILES'))
    SEARCHSTRING = 'rel[boundary=administrative](%s,%s,%s,%s);out;' % (map_details['min_latdeg'], map_details['min_lngdeg'], map_details['max_latdeg'], map_details['max_lngdeg'])  # search all cities in bounding box
    requests.session()
    r = requests.post(URL, data={'data': SEARCHSTRING})

    xmldoc = minidom.parseString(r._content)
    relations = xmldoc.getElementsByTagName('relation')
    
    osmids = [c.osmid for c in City.getCities()]
    cities = []
    for relation in relations:
        for tag in relation.childNodes:
            if tag.nodeName == "tag" and tag.attributes['k'].value == 'name':
                cities.append([relation.attributes['id'].value, tag.attributes['v'].value, int(relation.attributes['id'].value) in osmids])
    
    cities.sort(lambda x, y: cmp(x[1], y[1]))

    return render_template('admin.streets.city_osm.html', cities=cities)
