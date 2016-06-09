import os
import urllib2
import math
import re
import requests
from xml.dom import minidom
from PIL import Image, ImageDraw
from cStringIO import StringIO
from emonitor.extensions import signal, babel
from emonitor.socketserver import SocketHandler

CURRENTLOADING = []
LOADTILES = []


def getAlarmMap(alarm, tilepath, **params):
    """
    Build map for alarm as png image stream

    :param alarm: :py:class:`emonitor.modules.alarms.alarm.Alarm`
    :param tilepath: path to tile images
    :param params: dict with extra parameters
        - large = boolean, use large map (height =
    :return: image as stream
    """
    dimx = 5  # tiles in x dimension
    dimy = 3  # tiles in y dimension

    if 'style' in params and params['style'] == 'large':  # add height
        dimy += 1

    zoom = int(alarm.get('zoom', 18))
    img_map = Image.new('RGBA', (dimx * 256, dimy * 256), (255, 255, 255, 255))
    t = None
    try:
        t = deg2num(float(alarm.get('lat')), float(alarm.get('lng')), zoom)
    except ValueError:
        if alarm.object:
            t = deg2num(float(alarm.object.lat), float(alarm.object.lng), zoom)

    if not t:  # no position found, create default image
        stream = StringIO()
        draw = ImageDraw.Draw(img_map)
        draw.text((dimx * 256 / 2, dimy * 256 / 2), babel.gettext('alarms.position.notfound'), (255, 0, 0))
        img_map.save(stream, format="PNG", dpi=(600, 600))
        return stream.getvalue()

    cat = alarm.key.category
    items = []
    for itemtype in alarm.getMap().getMapItemDefinitions():
        for r in itemtype['key']:
            regex = re.compile(r)
            if regex.search(cat):
                items.append(itemtype)

    points = []
    if alarm.housenumber:
        def t2pixel(pt):
            deltax = pt[0] - t[0]  # tiles delta x
            deltay = pt[1] - t[1]  # tiles delta y

            x = dimx / 2 * 256 + (deltax * 256) + pt[2]
            y = dimy / 2 * 256 + (deltay * 256) + pt[3]
            return x, y

        for p in alarm.housenumber.points:
            points.append(t2pixel(deg2num(p[0], p[1], zoom)))

    for i in range(dimx / 2 * - 1, dimx / 2 + 1):
        for j in range(dimy / 2 * -1, dimy / 2 + 1):
            if not os.path.exists("{}{}/{}/{}-{}.png".format(tilepath, alarm.getMap().path, zoom, t[0] + i, t[1] + j)):
                from emonitor.tileserver.tileserver import getTilePath  # load tile from web
                getTilePath(alarm.getMap().path, zoom, t[0] + i, t[1] + j)
            img_tile = Image.open("{}{}/{}/{}-{}.png".format(tilepath, alarm.getMap().path, zoom, t[0] + i, t[1] + j))
            img_map.paste(img_tile, (dimx / 2 * 256 + (i * 256), dimy / 2 * 256 + (j * 256)))

            #if alarm.key.category.startswith('B'):
            for item in items:
                if item['parameters']['tileserver'] == '1':
                    if os.path.exists("{}{}/{}/{}-{}.png".format(tilepath, item['parameters']['layout'], zoom, t[0] + i, t[1] + j)):
                        img_tmp = Image.open("{}{}/{}/{}-{}.png".format(tilepath, item['parameters']['layout'], zoom, t[0] + i, t[1] + j))
                        img_map.paste(img_tmp, (dimx / 2 * 256 + (i * 256), dimy / 2 * 256 + (j * 256)), mask=img_tmp)

    if len(points) > 0:  # draw house
        poly = Image.new('RGBA', (dimx * 256, dimy * 256), (255, 255, 255, 0))
        pdraw = ImageDraw.Draw(poly)
        pdraw.polygon(points, fill=(255, 0, 0, 50), outline=(255, 0, 0, 255))
        img_map.paste(poly, mask=poly)

    stream = StringIO()
    img_map.save(stream, format="PNG", dpi=(600, 600))
    return stream.getvalue()


def getAlarmRoute(alarm, tilepath):
    """
    Build path for alarm as png image stream

    :param alarm: :py:class:`emonitor.modules.alarms.alarm.Alarm`
    :param tilepath: path to tile images
    :return: image as stream
    """
    from emonitor.tileserver.tileserver import getTileFromURL
    zoom = 18  # initial max zoom
    coords = alarm.getRouting()['coordinates']

    def getCoords(zoom):  # eval tiles for zoom factor
        tiles = {'lat': [], 'lng': []}
        for coord in coords:
            t = deg2num(coord[1], coord[0], zoom)
            if t[0] not in tiles['lat']:
                tiles['lat'].append(t[0])
            if t[1] not in tiles['lng']:
                tiles['lng'].append(t[1])
        tiles['lat'] = sorted(tiles['lat'])
        tiles['lng'] = sorted(tiles['lng'])
        tiles['lat'] = range(tiles['lat'][0] - 1, tiles['lat'][-1] + 3)
        tiles['lng'] = range(tiles['lng'][0] - 1, tiles['lng'][-1] + 3)

        if len(tiles['lat']) > 6:  # use zoom level lower
            zoom -= 1
            return getCoords(zoom)
        return tiles, zoom

    tiles, zoom = getCoords(zoom)

    # image map
    img_map = Image.new('RGBA', ((len(tiles['lat']) - 1) * 256, (len(tiles['lng']) - 1) * 256), (255, 255, 255, 255))
    for i in range(tiles['lat'][0], tiles['lat'][-1]):
        if alarm.getMap():
            for j in range(tiles['lng'][0], tiles['lng'][-1]):
                if not os.path.exists("{}{}/{}/{}-{}.png".format(tilepath, alarm.getMap().path, zoom, i, j)):
                    getTileFromURL(zoom, "{}{}/{}/{}-{}.png".format(tilepath, alarm.getMap().path, zoom, i, j), i, j)
                img_tile = Image.open("{}{}/{}/{}-{}.png".format(tilepath, alarm.getMap().path, zoom, i, j))
                img_map.paste(img_tile, (tiles['lat'].index(i) * 256, tiles['lng'].index(j) * 256))

    img_map = img_map.convert('LA').convert('RGBA')  # convert background to grayscale

    # image route
    img_route = Image.new('RGBA', ((len(tiles['lat']) - 1) * 256, (len(tiles['lng']) - 1) * 256), (255, 255, 255, 0))
    l = []
    for p in coords:
        t = deg2num(p[1], p[0], zoom)
        x = 256 * (t[0] - tiles['lat'][0]) + t[2]  # convert to absolute pixel coords
        y = 256 * (t[1] - tiles['lng'][0]) + t[3]
        l.append((x, y))
    for (s, e) in zip(l, l[1:])[2::]:  # route line in pixel
        line = ImageDraw.Draw(img_route)
        line.line([s, e], fill=(255, 0, 0, 100), width=10)

    img_map.paste(img_route, (0, 0), mask=img_route)  # add route to map
    img_map = img_map.crop((128, 128, img_map.size[0] - 128, img_map.size[1] - 128))
    stream = StringIO()
    img_map.save(stream, format="PNG", dpi=(300, 300))
    return stream.getvalue()


def loadTiles(path, tilelist):
    """
    Load map tiles into path from given tilelist

    :param path: path to store map tiles
    :param tilelist: list of tiles to load from OSM
    :return: progress information *[position, number of tiles to load]* as list
    """
    from emonitor.extensions import scheduler
    LOADTILES.append(tilelist[min(tilelist.keys())][0])  # add selected tile
    CURRENTLOADING.extend(sum(tilelist.values(), []))  # add tiles
    signal.send('map', 'tiledownloadstart', tiles=tilelist[min(tilelist.keys())][0])

    def doLoadTiles(**kwargs):

        def getTile(zoom, item):
            response = urllib2.urlopen('http://a.tile.openstreetmap.org/{}/{}/{}.png'.format(zoom, item[0], item[1]))
            with open('{}/{}/{}-{}.png'.format(path, zoom, item[0], item[1]), 'wb') as fout:
                fout.write(response.read())
            if item in CURRENTLOADING:
                CURRENTLOADING.remove(item)

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
            if not os.path.exists('{}/{}'.format(path, zoom)):
                os.makedirs('{}/{}'.format(path, zoom))
            for item in tilelist[zoom]:
                if len(CURRENTLOADING) == 0:  # loding stopped or ended
                    return
                if (len(LOADTILES) * 5460 - len(CURRENTLOADING)) % 10 == 0:  # send state every 10 loads
                    signal.send('map', 'tiledownloadprogress', progress=(len(LOADTILES) * 5460 - len(CURRENTLOADING), len(LOADTILES) * 5460), tiles=LOADTILES)
                try:
                    getTile(zoom, item)
                except:
                    errortiles.append((zoom, item))
        # try error objects
        for err in errortiles:
            try:
                getTile(err[0], err[1])
            except:
                print "error in {}".format(err)
        signal.send('map', 'tiledownloaddone', tiles=tilelist[min(tilelist.keys())][0])

    scheduler.add_job(doLoadTiles, kwargs={'path': path, 'tilelist': tilelist})
    return 1  # loading started


def deg2num(lat_deg, lon_deg, zoom):
    """Calculate tile coordinates and pixel position

    :param lat_deg: float value for latitude
    :param lon_deg: float value for longitude
    :param zoom: integer value of zoom level
    :return: list with x-tile, y-tile, x-pixel, y-pixel
    """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    x = (lon_deg + 180.0) / 360.0 * n
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    y = (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n
    return [xtile, ytile, int(x % 1 * 256), int(y % 1 * 256)]


def loadPositionOfCity(name):
    """
    Get position of city given by name

    :param name: name of city as string
    :return: dict with cities sorted by name
    """
    SEARCHSTRING = 'node["name"~"{}"]["place"~"town|village"];(._;>;);out;'.format(name.encode('utf-8'))  # search all cities with given name
    r = requests.post('http://overpass-api.de/api/interpreter', data={'data': SEARCHSTRING})
    cities = []
    xmldoc = minidom.parseString(r.content)
    for node in xmldoc.getElementsByTagName('node'):
        for tag in node.childNodes:
            if tag.nodeName == "tag" and tag.attributes['k'].value == 'name':
                cities.append(dict(name=tag.attributes['v'].value, lat=node.attributes['lat'].value, lon=node.attributes['lon'].value))
    return dict(result=sorted(cities, key=lambda k: k['name']))


class adminMapHandler(SocketHandler):
    """
    Handler class for admin socked events of maps
    """
    @staticmethod
    def handleMapDownloadStart(sender, **extra):
        """
        Implementation of start map tile download

        :param sender: event sender
        :param extra: extra parameters for event
        """
        SocketHandler.send_message(sender, **extra)

    @staticmethod
    def handleMapDownloadStop(sender, **extra):
        """
        Implementation of stop map tile download

        :param sender: event sender
        :param extra: extra parameters for event
        """
        SocketHandler.send_message(sender, **extra)

    @staticmethod
    def handleMapDownloadDone(sender, **extra):
        """
        Implementation of stop map tile download

        :param sender: event sender
        :param extra: extra parameters for event
        """
        if 'tiles' in extra and extra['tiles'] in LOADTILES:
            LOADTILES.remove(extra['tiles'])  # clicked tile, zoom 12
        SocketHandler.send_message(sender, **extra)

    @staticmethod
    def handleMapDownloadProgress(sender, **extra):
        """
        Implementation of stop map tile download

        :param sender: event sender
        :param extra: extra parameters for event
        """
        SocketHandler.send_message(sender, **extra)

if __name__ == "__main__":
    print deg2num(48.1083922, 11.7306440, 18)
