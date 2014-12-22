import os
from emonitor import webapp
from emonitor.modules.mapitems.mapitem import ItemLayout
from emonitor.modules.mapitems.mapitem_utils import deg2num
from emonitor.extensions import babel
from PIL import Image, ImageDraw

__all__ = ['LayoutFFEntry']
babel.gettext('mapitems.params.ffentry')


class LayoutFFEntry(ItemLayout):
    """LayoutFFEntry"""

    __name__ = 'ffentry'
    __version__ = '0.2'

    itemtype = 'way'
    filter = '[highway][service="emergency_access"]'
    attributes = ['id', 'lat', 'lon']

    ZOOMLEVELS = 16, 17, 18
    DESTPATH = '%s%s' % (webapp.config.get('PATH_TILES'), __name__)

    LINECOLOR = (255, 0, 0)  # yellow

    def buildTiles(self, items, attributes):
        """
        Build tiles of given items

        :param items: list of items to build
        :param attributes: attributes for layout
        """
        matrix = {}

        def addItem(tx, ty, px, py, **itemparams):
            if '%s|%s' % (tx, ty) not in matrix:
                matrix['%s|%s' % (tx, ty)] = []
            matrix['%s|%s' % (tx, ty)].append([px, py, itemparams])

        params = {}

        for zoom in self.ZOOMLEVELS:

            if not os.path.exists('%s/%s' % (self.DESTPATH, zoom)):  # create directory
                os.makedirs('%s/%s' % (self.DESTPATH, zoom))

            for item in items:
                _last = None
                for node in item.parameters['nodes']:
                    coord = deg2num(float(node['lat']), float(node['lon']), zoom)

                    if _last is not None:

                        if _last[0] <= coord[0]:  # eval tiles in x direction
                            dx = range(_last[0], coord[0] + 1)
                        else:
                            dx = range(_last[0], coord[0] - 1, -1)

                        if _last[1] <= coord[1]:  # eval tiles in y direction
                            dy = range(_last[1], coord[1] + 1)
                        else:
                            dy = range(_last[1], coord[1] - 1, -1)

                        for x in dx:  # loop through tiles
                            for y in dy:
                                lstart = (_last[2] + (_last[0] - x) * 256, _last[3] + (_last[1] - y) * 256)  # start point
                                lend = (coord[2] + (coord[0] - x) * 256, coord[3] + (coord[1] - y) * 256)  # end point

                                if os.path.exists('%s/%s/%s-%s.png' % (self.DESTPATH, zoom, x, y)):
                                    img = Image.open('%s/%s/%s-%s.png' % (self.DESTPATH, zoom, x, y))
                                else:
                                    img = Image.new('RGBA', (256, 256))
                                draw = ImageDraw.Draw(img)

                                draw.line([lstart, lend], fill=self.LINECOLOR, width=(zoom - 15) * 2)  # draw line
                                img.save('%s/%s/%s-%s.png' % (self.DESTPATH, zoom, x, y))

                    _last = coord
