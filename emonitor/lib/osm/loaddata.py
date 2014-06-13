import pickle
import time
from emonitor.lib.osm.OsmApi import OsmApi


def loadOsmData(**kwargs):
    i = 0
    
    if 'lat' in kwargs:
        lat = kwargs['lat']
    if 'lng' in kwargs:
        lng = kwargs['lng']
    if 'path' in kwargs:
        path = kwargs['path']

    MyApi = OsmApi(debug=True)
    for x in range(0, len(lat) - 1):
        for y in range(0, len(lng) - 1):
            pickle.dump(MyApi.Map(lng[y], lat[x], lng[y + 1], lat[x + 1]), open('%sosmdata%s.p' % (path, i), 'w'))
            i += 1

    return {'parts': i}


def parseOsmData(**kwargs):
    """load osm data and build dicts"""
    
    if 'lat' in kwargs:
        lat = kwargs['lat']
    if 'lng' in kwargs:
        lng = kwargs['lng']
    if 'path' in kwargs:
        path = kwargs['path']
    
    cities = {}
    streets = {}
    stime = time.time()
    MyApi = OsmApi(debug=True)
    
    for x in range(0, len(lat) - 1):
        for y in range(0, len(lng) - 1):
            for d in MyApi.Map(lng[y], lat[x], lng[y + 1], lat[x + 1]):

                if d['type'] == 'relation':  # city
                    if 'tag' in d['data'] and 'type' in d['data']['tag'] and 'name' in d['data']['tag'] and d['data']['tag']['type']=='boundary':
                        # load additional data of city
                        nodes = []
                        for member in d['data']['member']:  # member ways
                            try:
                                for m in MyApi.WayFull(member['ref']):  # load nodes
                                    if 'lat' in m['data']:
                                            nodes.append((m['data']['lat'], m['data']['lon']))
                                    else:  # node list
                                        try:
                                            if 'nd' in m['data']:
                                                for n in m['data']['nd']:
                                                    for node in MyApi.NodeGet(n):
                                                        nodes.append((node['lat'], node['lon']))
                                        except: pass
                            except: pass
 
                        if d['data']['id'] not in cities.keys():
                            cities[d['data']['id']] = {u'id': d['data']['id'], u'name': d['data']['tag']['name'], u'version': d['data']['version'], u'nodes': nodes}
                        else:
                            cities[d['data']['id']]['nodes'] += nodes
                            
                            #_cids.append(d['data']['id'])
                            #cities.append({u'id':d['data']['id'], u'name':d['data']['tag']['name'], u'version':d['data']['version'], u'nodes':nodes})
                
                if d['type'] == 'way':
                    if 'tag' in d['data'] and 'highway' in d['data']['tag'] and 'name' in d['data']['tag']:
                        nodes = []
                        
                        for m in MyApi.WayFull(d['data']['id']):
                            if 'lat' in m['data']:
                                nodes.append((m['data']['lat'], m['data']['lon']))
                            else:
                                try:
                                    if 'nd' in m['data']:
                                        for n in m['data']['nd']:
                                            for node in MyApi.NodeGet(n):
                                                nodes.append((node['lat'], node['lon']))
                                except: pass

                        #if 'nd' in d['data']: # load nodes
                        #    for n in d['data']['nd']:
                        #        node = MyApi.NodeGet(n)
                        #        nodes.append((node['lat'], node['lon']))
                        
                        #print "street", d['data']['tag']['name'], len(nodes)
                        
                        if d['data']['id'] not in streets.keys():
                            streets[d['data']['id']] = {u'id': d['data']['id'], u'name': d['data']['tag']['name'], u'version': d['data']['version'], u'nodes': nodes}
                        else:
                            streets[d['data']['id']]['nodes'] += nodes
                        
                        #if d['data']['id'] not in _sids:
                        #    _sids.append(d['data']['id'])
                        #    streets.append({u'id':d['data']['id'], u'name':d['data']['tag']['name'], u'version':d['data']['version'], u'nodes':nodes})
    print "found %s cities and %s streets" % (len(cities.keys()), len(streets.keys()))
    pickle.dump(cities.values(), open('%scities.p' % path, 'wb'))
    pickle.dump(streets.values(), open('%sstreets.p' % path, 'wb'))
    print "duration %s" % (time.time() - stime)