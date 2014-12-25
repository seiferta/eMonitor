import os, math, yaml
from emonitor.extensions import db, classes


class Settings(db.Model):
    __tablename__ = 'settings'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    _value = db.Column('value', db.Text)
    #value = db.Column(db.PickleType)

    def __init__(self, name, value=""):
        self.name = name
        self._value = value

    @property
    def value(self):
        return yaml.load(self._value)

    @value.setter
    def value(self, val):
        self._value = yaml.safe_dump(val, encoding='utf-8')

    @staticmethod
    def num2deg(xtile, ytile, zoom=db.app.config.get('DEFAULTZOOM')):
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_deg = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * ytile / n))))
        return lat_deg, lon_deg

    def getCarTypeNames(self):
        return self.value

    @staticmethod
    def getCarTypes():
        val = db.session.query(Settings).filter_by(name='cartypes').first()
        if val:
            return val.value
        return []

    @staticmethod
    def get_byType(type):
        return db.session.query(Settings).filter_by(name=type).first()

    @staticmethod
    def getMapTiles(mid=0, zoom=db.app.config.get('DEFAULTZOOM')):
        _map = classes.get('map').getMaps(mid)
        tiles = []
        try:
            for ts in [f for f in os.listdir(_map.path + str(zoom) + '/') if f.endswith('png')]:
                tiles.append(ts.replace('-', '/'))
        except:
            pass
        return tiles

    @staticmethod
    def getFrontendSettings(area=""):
        s = db.session.query(Settings).filter_by(name='frontend.default')
        if s.count() == 1:
            if area == "":
                return s.first().value
            elif area in s.first().value.keys():
                return s.first().value[area]
        return {'module': 'default', 'width': '.2', 'visible': '0', 'center': {'module': 'default'}, 'west': {'module': 'default', 'width': '.2'}, 'east': {'module': 'default', 'width': '.2'}}

    @staticmethod
    def get(option, default=''):  # getter for settings
        s = db.session.query(Settings).filter_by(name=option)
        if s.count() == 1:  # update
            return s.first().value
        return default  # deliver default value

    @staticmethod
    def set(option, val):  # setter for settings
        s = db.session.query(Settings).filter_by(name=option).first()
        if s:  # update settings
            s.value = val
        else:  # add value
            s = Settings(option, yaml.dump(val))
            db.session.add(s)
        db.session.commit()
        return s
