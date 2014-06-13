import sys
sys.path.append('.')

from emonitor.lib.osm.OsmApi import OsmApi
import pickle
import pprint



# overpass: http://overpass-turbo.eu/
# area[name="Haar"];way(area)[highway][name];(._;>;);out;

# area[name="Vaterstetten"];way(area)[highway][name];(._;>;);out;


   
def point_in_poly(x,y,poly):

    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside




def test():

    s_fin = open('d:/data/python/ffh/data2/streets.p', 'rb')
    c_fin = open('d:/data/python/ffh/data2/cities.p', 'rb')

    streets = pickle.load(s_fin)

    for city in [pickle.load(c_fin)[21]]: #543186
        print city['name'], city['id']
        for street in streets:
            if street['id']==23740589:
                print "---- ", street['name'], len(street['nodes'])
                for p in street['nodes']:
            #        #print p[0], p[1], city['nodes']
                    if point_in_poly(p[0], p[1], city['nodes']):
                        print street['name']
            
        #break
    
#test()
    
def rel():
    osmapi = OsmApi()
    
    #pprint.pprint(osmapi.RelationGet(543186))
    
    #pprint.pprint(osmapi.WayGet(26239346))
    
    pprint.pprint(osmapi.WayRelations(18801503))
    
    
    
print rel()
