import os
from PIL import Image, ImageDraw, ImageFont
from emonitor import webapp
from flask import flash
from emonitor.modules.mapitems.mapitem import ItemLayout
from emonitor.modules.mapitems.mapitem_utils import deg2num
from emonitor.extensions import babel

__all__ = ['LayoutHydrant']
babel.gettext('mapitems.params.hydrant')


class LayoutHydrant(ItemLayout):

    __name__ = 'hydrant'
    __version__ = '0.1'

    itemtype = 'node'
    filter = '[emergency="fire_hydrant"]'
    attributes = ['id', 'lat', 'lon', 'fire_hydrant:type', 'fire_hydrant:diameter']

    ZOOMLEVELS = 16, 17, 18
    DESTPATH = '%s%s' % (webapp.config.get('PATH_TILES'), __name__)

    HALFX = 10  # half icon width in pixels
    HALFY = 14  # half icon height in pixels

    def buildTiles(self, items, attributes):
        """Build tiles for given configuration

        :param items: mapitems with
        :param attributes: list of attributes
        matrix coords:
             1 | 2 | 3
            ___|___|___
             4 | 5 | 6
            ___|___|___
             7 | 8 | 9
        """
        font = ImageFont.truetype("emonitor/modules/mapitems/inc/font.ttf", 12)

        for zoom in self.ZOOMLEVELS:
            matrix = {}
            if not os.path.exists('%s/%s' % (self.DESTPATH, zoom)):
                os.makedirs('%s/%s' % (self.DESTPATH, zoom))

            for item in items:
                coord = deg2num(float(item.parameters['lat']), float(item.parameters['lon']), zoom)

                def addItem(tx, ty, px, py, **itemparams):
                    if '%s|%s' % (tx, ty) not in matrix:
                        matrix['%s|%s' % (tx, ty)] = []
                    matrix['%s|%s' % (tx, ty)].append([px, py, itemparams])

                params = {}
                for param in [a for a in attributes if a in item.parameters]:
                    params[param] = item.parameters[param]

                addItem(coord[0], coord[1], coord[2], coord[3], params=params)  # q5
                if coord[2] + self.HALFX > 256:
                    addItem(coord[0] + 1, coord[1], coord[2] - 256, coord[3], params=params)  # q6
                if coord[2] - self.HALFX < 0:
                    addItem(coord[0] - 1, coord[1], coord[2] + 256, coord[3], params=params)  # q4
                if coord[3] + self.HALFY > 256:
                    addItem(coord[0], coord[1] + 1, coord[2], coord[3] - 256, params=params)  # q8
                if coord[3] - self.HALFY < 0:
                    addItem(coord[0], coord[1] - 1, coord[2], coord[3] + 256, params=params)  # q2
                if coord[2] + self.HALFX > 256 and coord[3] + self.HALFY > 256:
                    addItem(coord[0] + 1, coord[1] + 1, coord[2] - 256, coord[3] - 256, params=params)  # q9
                elif coord[2] - self.HALFX < 0 and coord[3] - self.HALFY < 0:
                    addItem(coord[0] - 1, coord[1] - 1, coord[2] + 256, coord[3] + 256, params=params)  # q1

            for tile in matrix:
                img = Image.new('RGBA', (256, 256))
                draw = ImageDraw.Draw(img)

                if zoom == 18:
                    """
                    icon=ellipse;20;20 # objecttype, x dimension, y dimension
                    color=255;0;0
                    textattribute=fire_hydrant:diameter
                    """
                    for p in matrix[tile]:
                        draw.ellipse((p[0] - 10, p[1] - 10, p[0] + 10, p[1] + 10), outline=(255, 0, 0))
                        if 'fire_hydrant:diameter' in p[2]['params']:
                            draw.text((p[0] - self.HALFX, p[1] + self.HALFY), "%s" % p[2]['params']['fire_hydrant:diameter'], (255, 0, 0), font=font)
                if zoom == 17:
                    """
                    icon=ellipse;10;10 # objecttype, x dimension, y dimension
                    color=255;0;0 # rgb color value
                    """
                    for p in matrix[tile]:
                        draw.ellipse((p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5), fill=(255, 0, 0))
                if zoom == 16:
                    """
                    icon=ellipse;4;4 # objecttype, x dimension, y dimension
                    color=255;0;0 # rgb color value
                    """
                    for p in matrix[tile]:
                        draw.ellipse((p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2), fill=(255, 0, 0))

                img.save('%s/%s/%s-%s.png' % (self.DESTPATH, zoom, tile.split('|')[0], tile.split('|')[1]))
