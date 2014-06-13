import math


IMAGE_X = 24
IMAGE_Y = 40


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


def buildTiles(tiletype, levels):
    """Build tiles for given configuration

    :param tiletype: typeobject, needed for path==name and parameters
    :param levels: list with zoom levels

    parameters:
        <pre>
        [17]
        icon=ellipse;20;20 # objecttype, x dDimension, y dimension
        color=255;0;0 # rgb color value
        textattribute=

        [18]
        icon=ellipse;20;20
        color=255;0;0
        textattribute=fire_hydrant:diameter
        </pre>

    matrix coords:
         1 | 2 | 3
        ___|___|___
         4 | 5 | 6
        ___|___|___
         7 | 8 | 9
    """
    #import sys
    import os
    from PIL import Image, ImageDraw, ImageFont
    #sys.path.append('.')

    from emonitor.extensions import classes
    from emonitor import webapp

    DESTPATH = '%s%s' % (webapp.config.get('PATH_TILES'), tiletype['name'])
    HALFX = 10
    HALFY = 14

    items = classes.get('mapitem').getMapitems(tiletype['name'])
    font = ImageFont.truetype("emonitor/modules/mapitems/inc/font.ttf", 12)

    for zoom in levels:
        matrix = {}
        if not os.path.exists('%s/%s' % (DESTPATH, zoom)):
            os.makedirs('%s/%s' % (DESTPATH, zoom))

        for item in items:
            coord = deg2num(float(item.parameters['lat']), float(item.parameters['lon']), zoom)

            def addItem(tx, ty, px, py, **itemparams):
                if '%s|%s' % (tx, ty) not in matrix:
                    matrix['%s|%s' % (tx, ty)] = []
                matrix['%s|%s' % (tx, ty)].append([px, py, itemparams])

            #diameter = ' '
            #if 'fire_hydrant:diameter' in item.parameters.keys():
            #    diameter = item.parameters['fire_hydrant:diameter']

            params = {}
            for param in tiletype['attributes']:
                if param in item.parameters:
                    params[param] = item.parameters[param]

            addItem(coord[0], coord[1], coord[2], coord[3], params=params)  # q5
            if coord[2] + HALFX > 256:
                addItem(coord[0] + 1, coord[1], coord[2] - 256, coord[3], params=params)  # q6
            if coord[2] - HALFX < 0:
                addItem(coord[0] - 1, coord[1], coord[2] + 256, coord[3], params=params)  # q4
            if coord[3] + HALFY > 256:
                addItem(coord[0], coord[1] + 1, coord[2], coord[3] - 256, params=params)  # q8
            if coord[3] - HALFY < 0:
                addItem(coord[0], coord[1] - 1, coord[2], coord[3] + 256, params=params)  # q2
            if coord[2] + HALFX > 256 and coord[3] + HALFY > 256:
                addItem(coord[0] + 1, coord[1] + 1, coord[2] - 256, coord[3] - 256, params=params)  # q9
            elif coord[2] - HALFX < 0 and coord[3] - HALFY < 0:
                addItem(coord[0] - 1, coord[1] - 1, coord[2] + 256, coord[3] + 256, params=params)  # q1

        if tiletype['parameters']['layout'] == 'hydrant':  # create tiles for layout hydrant
            for tile in matrix:
                img = Image.new('RGBA', (256, 256))
                draw = ImageDraw.Draw(img)

                if zoom == 18:
                    for p in matrix[tile]:
                        draw.ellipse((p[0] - 10, p[1] - 10, p[0] + 10, p[1] + 10), outline=(255, 0, 0))
                        if 'fire_hydrant:diameter' in p[2]['params']:
                            draw.text((p[0] - HALFX, p[1] + HALFY), "%s" % p[2]['params']['fire_hydrant:diameter'], (255, 0, 0), font=font)
                if zoom == 17:
                    for p in matrix[tile]:
                        draw.ellipse((p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5), fill=(255, 0, 0))
                if zoom == 16:
                    for p in matrix[tile]:
                        draw.ellipse((p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2), fill=(255, 0, 0))

                img.save('%s/%s/%s-%s.png' % (DESTPATH, zoom, tile.split('|')[0], tile.split('|')[1]))

        else:
            print "layout definition not found"


if __name__ == "__main__":
    import sys
    sys.path.append('.')
    from emonitor.extensions import classes
    print classes.get('settings').get('mapitemdefinition')
    itemtype = [t for t in classes.get('settings').get('mapitemdefinition') if t['name'] == 'Hydranten'][0]
    buildTiles(itemtype, [16, 17, 18])