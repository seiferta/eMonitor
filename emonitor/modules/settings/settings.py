import os, math, yaml
from emonitor.extensions import db


class Settings(db.Model):
    """Settings class"""
    __tablename__ = 'settings'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    _value = db.Column('value', db.Text)

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
    def num2deg(xtile, ytile, zoom=17 or db.config.get('DEFAULTZOOM')):
        """
        Translate tile into coordinate (lat, lon)

        :param xtile: x-coordinate of tile
        :param ytile: y-coordinate of tile
        :param zoom: zoom level
        :return: lat, lon tuple
        """
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_deg = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * ytile / n))))
        return lat_deg, lon_deg

    def getCarTypeNames(self):
        return self.value

    @staticmethod
    def getCarTypes():
        return Settings.query.filter_by(name='cartypes').one().value

    @staticmethod
    def get_byType(type):
        return Settings.query.filter_by(name=type).first() or ""

    @staticmethod
    def getMapTiles(mid=0, zoom=17 or db.app.config.get('DEFAULTZOOM')):
        from emonitor.modules.maps.map import Map
        _map = Map.getMaps(mid)
        tiles = []
        try:
            for ts in [f for f in os.listdir(_map.path + str(zoom) + '/') if f.endswith('png')]:
                tiles.append(ts.replace('-', '/'))
        except:
            pass
        return tiles

    @staticmethod
    def getFrontendSettings(area=""):
        s = Settings.query.filter_by(name='frontend.default')
        if s.count() == 1:
            if area == "":
                return s.first().value
            elif area in s.first().value.keys():
                return s.first().value[area]
        return {'module': 'default', 'width': '.2', 'visible': '0', 'center': {'module': 'default'}, 'west': {'module': 'default', 'width': '.2'}, 'east': {'module': 'default', 'width': '.2'}}

    @staticmethod
    def get(option, default=''):
        """
        Getter for option values

        :param option: name as string
        :param optional default: default value if not found in database
        :return: value of option
        """
        s = Settings.query.filter_by(name=option)
        if s.count() == 1:  # update
            return s.first().value
        return default  # deliver default value

    @staticmethod
    def set(option, val):
        """
        Setter for option

        :param option: name as string
        :param val: value of option
        :return: value of option
        """
        s = Settings.query.filter_by(name=option).first()
        if s:  # update settings
            s.value = val
        else:  # add value
            s = Settings(option, yaml.dump(val))
            db.session.add(s)
        db.session.commit()
        return s

    @staticmethod
    def getIntList(option, default=[]):
        try:
            return map(int, Settings.get(option, '').split(','))
        except ValueError:
            return default
