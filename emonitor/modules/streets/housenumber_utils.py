import requests
from xml.dom import minidom
from emonitor.extensions import classes

URL = 'http://overpass-api.de/api/interpreter'


def loadHousenumbersFromOsm(streets):  # load all housenumbers from osm
    global URL
    housenumbers = {}
    for street in streets:
        city = classes.get('city').get_byid(street.cityid)
        SEARCHSTRING = 'area[name="%s"];way(area)[building]["addr:street"="%s"];(._;>;);out;' % (city.name, street.name)
        r = requests.post(URL, data={'data': SEARCHSTRING})
        xmldoc = minidom.parseString(r._content)
        nodes = {}
        for node in xmldoc.getElementsByTagName('node'):
            nodes[node.attributes['id'].value] = [float(node.attributes['lat'].value), float(node.attributes['lon'].value)]

        # try with associatedStreet
        SEARCHSTRING = 'area[name="%s"];rel[type=associatedStreet](area)->.allASRelations;way(r.allASRelations:"street")[name="%s"];rel(bw:"street")[type=associatedStreet]->.relationsWithRoleStreet;way(r.relationsWithRoleStreet)[building];(._;>;);out;' % (city.name, street.name)
        r = requests.post(URL, data={'data': SEARCHSTRING})
        xmldoc = minidom.parseString(r._content)
        for node in xmldoc.getElementsByTagName('node'):
            nodes[node.attributes['id'].value] = [float(node.attributes['lat'].value), float(node.attributes['lon'].value)]

        for way in xmldoc.getElementsByTagName('way'):
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
    return len(housenumbers)