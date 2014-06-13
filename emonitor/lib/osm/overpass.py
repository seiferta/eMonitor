
import requests
import pprint
from xml.dom import minidom


def loadStreetsOfCity(cityname):
    
    URL = 'http://overpass-api.de/api/interpreter'
    
    SEARCHSTRING = """area[name="Haar"];way(area)[highway][name];(._;>;);out;""" # search all streets of haar
    #SEARCHSTRING = """rel[boundary=administrative](48.0,11.68,48.16,11.86);out;""" # search all cities in bounding box
    
    payload = {
        'data': SEARCHSTRING
    }

    session = requests.session()
    r = requests.post(URL, data=payload)
    
    fout = open('d:/data/python/ffh/data2/streets_haar.xml', 'w')
    fout.write( r._content)
    fout.close()
    
        
    
#loadStreetsOfCity('')


def parseData():
    
    data = open('d:/data/python/ffh/data2/cities.xml', 'r').read()
    
    
    xmldoc = minidom.parseString(data)
    relations = xmldoc.getElementsByTagName('relation') 

    for relation in relations :
        for tag in relation.childNodes:
            if tag.nodeName=="tag" and tag.attributes['k'].value=='name':
                print tag.attributes['v'].value, relation.attributes['id'].value



        
#parseData()



import itertools as IT

def centroid_of_polygon(points):
    """
    http://stackoverflow.com/a/14115494/190597 (mgamba)
    """
    def area_of_polygon(x, y):
        """Calculates the signed area of an arbitrary polygon given its verticies
        http://stackoverflow.com/a/4682656/190597 (Joe Kington)
        http://softsurfer.com/Archive/algorithm_0101/algorithm_0101.htm#2D%20Polygons
        """
        area = 0.0
        for i in xrange(-1, len(x) - 1):
            area += x[i] * (y[i + 1] - y[i - 1])
        return area / 2.0

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
    return (result_x, result_y)







def parseData2():
    
    data = open('d:/data/python/ffh/data2/streets_haar.xml', 'r').read()
    
    
    xmldoc = minidom.parseString(data)
    nodes = xmldoc.getElementsByTagName('node') 
    ways = xmldoc.getElementsByTagName('way') 
    
    streets = {}
    n = {}
    
    for node in nodes:
        n[int(node.attributes['id'].value)] = (float(node.attributes['lat'].value), float(node.attributes['lon'].value))

    for way in ways:
        nds = []
        osmids = []
        name = ""
        for tag in way.childNodes:

            if tag.nodeName=="tag" and tag.attributes['k'].value=='name':
                name = tag.attributes['v'].value
                osmids.append(int(way.attributes['id'].value))
                
            if tag.nodeName=="nd":
                _nid = int(tag.attributes['ref'].value)
                if _nid in n.keys():
                    nds.append(n[_nid])
                
        if name not in streets.keys():
            streets[name] = {'osmids':osmids, 'nodes':nds}
        else:
            streets[name]['osmids'].extend(osmids)
            streets[name]['nodes'].extend(nds)

    for name in streets:
        
        points = streets[name]['nodes']
        if len(points)>2:
            cent = centroid_of_polygon(points)
            print name, cent 
        else:
            print name, points



        
parseData2()