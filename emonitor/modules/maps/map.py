import os
from emonitor.extensions import db, classes

DEFAULTZOOM = 12


class Map(db.Model):
    __tablename__ = 'maps'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    path = db.Column(db.String(128))
    maptype = db.Column(db.Integer, default=0)
    tileserver = db.Column(db.Text)
    default = db.Column(db.Integer, default=0)

    def __init__(self, name, path, maptype=0, tileserver="", default=0):
        self.name = name
        self.path = path
        self.maptype = maptype
        self.tileserver = tileserver
        self.default = default

    def getMapItems(self, itemtype=""):
        return classes.get('mapitems').getMapitems(itemtype)

    def getMapItemDefinitions(self):
        return classes.get('settings').get('mapitemdefinition')

    @staticmethod
    def getMapBox(tilepath="", mappath="", zoom=DEFAULTZOOM):
        ret = dict(mappath=[], coord=[], min_lngtile=10000, min_lattile=10000, max_lngtile=0, max_lattile=0,
                   min_lngdeg=0.0, max_lngdeg=0.0, min_latdeg=0.0, max_latdeg=0.0)

        for path, dirs, files in os.walk('%s%s' % (tilepath, mappath)):
            if path.endswith('/%s' % zoom) or path.endswith('\\%s' % zoom):
                for _file in files:
                    lat, lng = _file.split(".")[0].split('-')
                    # build bounding box
                    if int(lat) < ret['min_lattile']: ret['min_lattile'] = int(lat)
                    if int(lat) > ret['max_lattile']: ret['max_lattile'] = int(lat)
                    if int(lng) < ret['min_lngtile']: ret['min_lngtile'] = int(lng)
                    if int(lng) > ret['max_lngtile']: ret['max_lngtile'] = int(lng)

                    lat1, lng1 = classes.get('settings').num2deg(ret['min_lattile'], ret['min_lngtile'], zoom)
                    lat2, lng2 = classes.get('settings').num2deg(ret['max_lattile'] + 1, ret['max_lngtile'] + 1, zoom)

                    lat = [lat1, lat2]
                    lng = [lng1, lng2]
                    lat.sort()
                    lng.sort()

                    ret['min_latdeg'] = lat[0]
                    ret['max_latdeg'] = lat[-1]
                    ret['min_lngdeg'] = lng[0]
                    ret['max_lngdeg'] = lng[-1]

                    ret['mappath'].append(_file.replace('-', '/'))
                    ret['coord'].append('.'.join(_file.split('.')[:-1]))
                break
        return ret

    @staticmethod
    def getMaps(id=0):
        if id != 0:
            return db.session.query(Map).filter_by(id=id).first()
        else:
            return db.session.query(Map).all()

    @staticmethod
    def getDefaultMap():
        return db.session.query(Map).filter_by(default=1).first()