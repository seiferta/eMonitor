from flask import Blueprint, send_from_directory, current_app, make_response
from emonitor.modules.maps.map import Map
import os.path

tileserver = Blueprint('tileserver', __name__)


@tileserver.route('/tileserver/<string:maptype>/<int:zoom>/<int:lat>/<int:lng>')
def tileServer(maptype='', zoom=0, lat=0, lng=0):
    path, filename = getTilePath(maptype, zoom, lat, lng)

    resp = make_response(send_from_directory(path, filename))
    resp.cache_control.no_cache = True
    return resp


def getTileFromURL(zoom, filename, lat, lng):
    """ path example: /tileserver/osmap/14/8724/5688 """
    import urllib2
    response = urllib2.urlopen('http://a.tile.openstreetmap.org/%s/%s/%s.png' % (zoom, lat, lng))
    if not(os.path.exists(os.path.dirname(filename))):
        os.makedirs(os.path.dirname(filename))
    fout = open(filename, 'wb')
    fout.write(response.read())
    fout.close()


def getTilePath(mappath, zoom, lat, lng):
    """ deliver filepath to seleceted tile """
    #global mappath
    if not mappath:
        mappath = Map.getMaps()[0].path
    path = "%s%s/%s/" % (current_app.config.get('PATH_TILES'), mappath, zoom)
    filename = "%s-%s.png" % (lat, lng)
    
    if not os.path.exists('%s/%s' % (path, filename)):  # deliver default tile
        #current_app.logger.error('tileserver: tile not found %s%s using default' % (path, filename))
        if current_app.config.get('TILE_MISSING') == 'load' and "osm" in path:  # load tile from url
            getTileFromURL(zoom, path + filename, lat, lng)
            return path, filename
        else:
            return current_app.config.get('PATH_DATA'), 'default.png'
    else:
        return path, filename
