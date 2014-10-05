import requests
from xml.dom import minidom
import itertools as IT
from collections import OrderedDict

from flask import render_template, current_app
from emonitor.modules.maps.map import Map
from emonitor.modules.streets.city import City


def centroid_of_polygon(points):
    """
    http://stackoverflow.com/a/14115494/190597 (mgamba)
    """
    def area_of_polygon(x, y):
        """Calculates the signed area of an arbitrary polygon given its verticies
        http://stackoverflow.com/a/4682656/190597 (Joe Kington)
        http://softsurfer.com/Archive/algorithm_0101/algorithm_0101.htm#2D%20Polygons
        """
        _area = 0.0
        for _i in xrange(-1, len(x) - 1):
            _area += x[_i] * (y[_i + 1] - y[_i - 1])
        return _area / 2.0

    area = area_of_polygon(*zip(*points))
    result_x = 0
    result_y = 0
    N = len(points)
    points = IT.cycle(points)
    x1, y1 = next(points)
    for i in range(N):
        x0, y0 = x1, y1
        x1, y1 = next(points)
        cross = (x0 * y1) - (x1 * y0)
        result_x += (x0 + x1) * cross
        result_y += (y0 + y1) * cross
    result_x /= (area * 6.0)
    result_y /= (area * 6.0)
    return result_x, result_y

    
URL = 'http://overpass-api.de/api/interpreter'


def loadStreetsFromOsm(city=None, _format="html"):  # load all streets of given city
    global URL
    
    if not city:
        city = City.getDefaultCity()

    map_details = Map.getDefaultMap().getMapBox(tilepath=current_app.config.get('PATH_TILES'))

    SEARCHSTRING = 'area[name~"%s"];way(%s,%s,%s,%s)(area)[highway][name];(._;>;);out;' % (city.name, map_details['min_latdeg'], map_details['min_lngdeg'], map_details['max_latdeg'], map_details['max_lngdeg'])  # search all streets for given city
    r = requests.post(URL, data={'data': SEARCHSTRING})
    xmldoc = minidom.parseString(r.content)
    nodes = xmldoc.getElementsByTagName('node') 
    ways = xmldoc.getElementsByTagName('way')

    dbosmids = [int(s.osmid) for s in city.getStreets()]
    
    streets = OrderedDict()
    n = {}
    
    for node in nodes:
        n[int(node.attributes['id'].value)] = (float(node.attributes['lat'].value), float(node.attributes['lon'].value))

    for way in ways:
        nds = []
        osmids = []
        name = ""
        for tag in way.childNodes:

            if tag.nodeName == "tag" and tag.attributes['k'].value == 'name':
                name = tag.attributes['v'].value
                osmids.append(int(way.attributes['id'].value))
                
            if tag.nodeName == "nd":
                _nid = int(tag.attributes['ref'].value)
                if _nid in n.keys():
                    nds.append(n[_nid])
                
        if name not in streets.keys():
            streets[name] = {'osmids': osmids, 'nodes': nds, 'indb': False}
        else:
            streets[name]['osmids'].extend(osmids)
            streets[name]['nodes'].extend(nds)

        if len(set(osmids).intersection(set(dbosmids))) > 0:
            streets[name]['indb'] = True

    streets = OrderedDict(sorted(streets.items(), key=lambda t: t[0]))
    if _format == "html":  # html output
        return render_template('admin.streets_osm.html', streets=streets, city=city)
    else:  # data output
        for name in streets:
            points = streets[name]['nodes']
            if len(points) > 2:
                cent = centroid_of_polygon(points)
                streets[name]['center'] = cent
            elif len(points) == 2:
                streets[name]['center'] = (((points[0][0] + points[1][0]) / 2), ((points[0][1] + points[1][1]) / 2))
            else:
                streets[name]['center'] = (0.0, 0.0)
        return streets
