import os
import urllib2
import time, datetime
from emonitor.extensions import scheduler

LOADINPROGRESS = [0, 0]  # [_todo_, _done_]


def loadTiles(path, tilelist):
    global LOADINPROGRESS
    
    def doLoadTiles(**kwargs):
        global LOADINPROGRESS
        
        def getTile(zoom, item):
            response = urllib2.urlopen('http://a.tile.openstreetmap.org/%s/%s/%s.png' % (zoom, item[0], item[1]))
            LOADINPROGRESS[1] += 1
            #print "get", LOADINPROGRESS[1]
            with open('%s/%s/%s-%s.png' % (path, zoom, item[0], item[1]), 'wb') as fout:
                fout.write(response.read())
        if 'path' in kwargs:
            path = kwargs['path']
        else:
            return
            
        if 'tilelist' in kwargs:
            tilelist = kwargs['tilelist']
        else:
            return

        errortiles = []

        for zoom in tilelist:
            if not os.path.exists('%s/%s' % (path, zoom)):
                os.makedirs('%s/%s' % (path, zoom))
            for item in tilelist[zoom]:
                try:
                    getTile(zoom, item)
                except:
                    errortiles.append((zoom, item))
        # try error objects
        for err in errortiles:
            try:
                getTile(err[0], err[1])
            except:
                print "error in %s" % err
            
        LOADINPROGRESS = [0, 0]
    
    if LOADINPROGRESS[0] != 0:
        return LOADINPROGRESS  # still in progress
    
    LOADINPROGRESS = [sum(map(lambda x:len(tilelist[x]), tilelist)), 0]  # init progress
    scheduler.add_job(doLoadTiles, next_run_time=datetime.datetime.fromtimestamp(time.time() + 2), kwargs={'path': path, 'tilelist': tilelist})
    return 1  # loading started
