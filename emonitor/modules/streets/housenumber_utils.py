import requests
from xml.dom import minidom
from emonitor.extensions import signal
from emonitor.modules.streets.city import City

URL = 'http://overpass-api.de/api/interpreter'
"""url for data download from OpenStreetMap (overpass)"""


def loadHousenumbersFromOsm(streets):  # load all housenumbers from osm
    """
    Load all housenumbers of given street from OpenStreetMap

    :param streets: list of :py:class:`emonitor.modules.streets.street.Street`
    :return: number of housenumbers of given streeet
    """
    global URL
    housenumbers = {}
    for street in streets:
        nodes = {}
        ways = []
        city = City.getCities(id=street.cityid)
        SEARCHSTRING = 'area[name~"%s"];way(area)[building]["addr:street"="%s"];(._;>;);out;' % (city.osmname, street.name)
        r = requests.post(URL, data={'data': SEARCHSTRING})
        xmldoc = minidom.parseString(r.content)
        for node in xmldoc.getElementsByTagName('node'):
            nodes[node.attributes['id'].value] = [float(node.attributes['lat'].value), float(node.attributes['lon'].value)]
        for way in xmldoc.getElementsByTagName('way'):
            ways.append(way)

        # try with associatedStreet
        SEARCHSTRING = 'area[name~"%s"];rel[type=associatedStreet](area)->.allASRelations;way(r.allASRelations:"street")[name="%s"];rel(bw:"street")[type=associatedStreet]->.relationsWithRoleStreet;way(r.relationsWithRoleStreet)[building];(._;>;);out;' % (city.osmname, street.name)
        r = requests.post(URL, data={'data': SEARCHSTRING})
        xmldoc = minidom.parseString(r.content)
        for node in xmldoc.getElementsByTagName('node'):
            nodes[node.attributes['id'].value] = [float(node.attributes['lat'].value), float(node.attributes['lon'].value)]
        for way in xmldoc.getElementsByTagName('way'):
            ways.append(way)

        _numbers = 0
        for way in ways:
            nd = []
            _id = None
            for c in way.childNodes:
                if c.nodeName == "nd":
                    nd.append(nodes[c.attributes['ref'].value])
                if c.nodeName == "tag" and c.attributes['k'].value == 'addr:housenumber':
                    _id = c.attributes['v'].value
            if _id:
                housenumbers[_id] = nd
                street.addHouseNumber(_id, housenumbers[_id])
                _numbers += 1
        signal.send('housenumber', 'osm', street=street.name, hnumbers=_numbers, position=(streets.index(street) + 1, len(streets)), cityid=city.id)
    signal.send('housenumber', 'osmdone', numbers=len(housenumbers))
    return len(housenumbers)
