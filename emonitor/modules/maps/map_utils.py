import os
import urllib2
import math
import re
from PIL import Image, ImageDraw
from cStringIO import StringIO

LOADINPROGRESS = [0, 0]  # [_todo_, _done_]


def getAlarmMap(alarm, tilepath):
    dimx = 5  # tiles in x dimension
    dimy = 3  # tiles in y dimension
    zoom = int(alarm.get('zoom', 18))
    img_map = Image.new('RGBA', (dimx * 256, dimy * 256), (255, 255, 255, 255))
    t = deg2num(float(alarm.get('lat')), float(alarm.get('lng')), zoom)

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
            points.append(t2pixel(deg2num(p[0], p[1], 18)))

    for i in range(dimx / 2 * - 1, dimx / 2 + 1):
        for j in range(dimy / 2 * -1, dimy / 2 + 1):
            img_tile = Image.open("%s%s/%s/%s-%s.png" % (tilepath, alarm.getMap().path, zoom, t[0] + i, t[1] + j))
            img_map.paste(img_tile, (dimx / 2 * 256 + (i * 256), dimy / 2 * 256 + (j * 256)))

            #if alarm.key.category.startswith('B'):
            for item in items:
                if item['parameters']['tileserver'] == '1':
                    if os.path.exists("%s%s/%s/%s-%s.png" % (tilepath, item['name'], zoom, t[0] + i, t[1] + j)):
                        img_tmp = Image.open("%s%s/%s/%s-%s.png" % (tilepath, item['name'], zoom, t[0] + i, t[1] + j))
                        img_map.paste(img_tmp, (dimx / 2 * 256 + (i * 256), dimy / 2 * 256 + (j * 256)), mask=img_tmp)

    if len(points) > 0:  # draw house
        poly = Image.new('RGBA', (dimx * 256, dimy * 256), (255, 255, 255, 0))
        pdraw = ImageDraw.Draw(poly)
        pdraw.polygon(points, fill=(255, 0, 0, 50), outline=(255, 0, 0, 255))
        img_map.paste(poly, mask=poly)

    stream = StringIO()
    #img_map = img_map.resize((640, 364), Image.ANTIALIAS)
    img_map.save(stream, format="PNG", dpi=(600, 600))
    return stream.getvalue()


def loadTiles(path, tilelist):
    from emonitor.extensions import scheduler
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
    scheduler.add_single_job(doLoadTiles, kwargs={'path': path, 'tilelist': tilelist})
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


def deg2num_old(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    x = (lon_deg + 180.0) / 360.0 * n
    print "x", x, x % 1 * 256
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    y = (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n
    print "y", y, y % 1 * 256
    return xtile, ytile


if __name__ == "__main__":
    print deg2num(48.1083922, 11.7306440, 18)