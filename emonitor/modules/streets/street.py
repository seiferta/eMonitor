import yaml
from sqlalchemy.orm import relationship
from emonitor.extensions import db
from emonitor.modules.streets.housenumber import Housenumber
from emonitor.widget.monitorwidget import MonitorWidget


class Street(db.Model):
    """Street class"""
    __tablename__ = 'streets'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    navigation = db.Column(db.Text)
    cityid = db.Column(db.Integer, db.ForeignKey('cities.id'))
    subcity = db.Column(db.String(40))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    zoom = db.Column(db.Integer)
    active = db.Column(db.Integer, default=0)
    osmid = db.Column(db.Integer, default=0)

    city = relationship("City", backref="cities", lazy='joined')
    housenumbers = relationship(Housenumber.__name__, backref="streets", lazy='subquery', order_by=Housenumber.number)

    def __init__(self, name, navigation, cityid, subcity, lat, lng, zoom, active, osmid):
        self.name = name
        self.navigation = navigation
        self.cityid = cityid
        self.subcity = subcity
        self.lat = lat
        self.lng = lng
        self.zoom = zoom
        self.active = active
        self.osmid = osmid
        
    def __repr__(self):
        return '<Street %r - %r>' % (self.id, self.name)

    @property
    def serialize(self):
        """
        Serialize street object for json calls

        :return: dict with street attributes
        """
        return dict(id=self.id, name=self.name, city=self.city.serialize, subcity=self.subcity, lat=self.lat, lng=self.lng, zoom=self.zoom, active=self.active)

    def addHouseNumber(self, number, points):
        """
        Add housenumber for street

        :param number: housenumber as string
        :param points: list of points for housenumber
        """
        if number not in [hn.number for hn in self.housenumbers]:
            db.session.add(Housenumber(self.id, number, yaml.dump(points)))
            db.session.commit()

    def getHouseNumber(self, **kwargs):
        ret = []
        if "id" in kwargs:
            ret = filter(lambda x: x.id == kwargs['id'], self.housenumbers)
        elif "number" in kwargs:
            ret = filter(lambda x: x.number == kwargs['number'], self.housenumbers)
        if len(ret) > 0:
            return ret[0]
        return None

    @staticmethod
    def getStreets(id=0, cityid=0):
        """
        Get all streets of city given by id, *0* for all streets

        :param optional id: id of street, *0* for all
        :param optional cityid: id of city, *0* for all
        :return: list of :py:class:`emonitor.modules.streets.street.Street`
        """
        if id != 0:
            return Street.query.filter_by(id=id).one()
        if cityid != 0:
            return Street.query.filter_by(cityid=cityid).order_by(Street.name).all()
        else:
            return Street.query.order_by(Street.name).all()

    @staticmethod
    def getStreetsDict():
        """
        Get dict of streets, id as key

        :return: cict of :py:class:`emonitor.modules.streets.street.Street`
        """
        ret = dict(db.get(Street.id, Street).filter_by(active=1).order_by(Street.name))
        ret[0] = Street('', '', 0, '', 0, 0, 0, 1, 0)
        return ret


class StreetWidget(MonitorWidget):
    """Street widget for alarms"""
    template = 'widget.street.html'
    size = (2, 1)

    def addParameters(self, **kwargs):
        self.params.update(kwargs)
