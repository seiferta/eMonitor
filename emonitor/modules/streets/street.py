import yaml
from sqlalchemy.orm import relationship
from emonitor.extensions import db
from emonitor.modules.streets.housenumber import Housenumber


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

    @staticmethod
    def getStreet(id=0):
        """
        Get list of streets filtered by parameter

        :param optional id: id of street, *0* for all
        :return: list of :py:class:`emonitor.modules.streets.street.Street`
        """
        try:
            if int(id):
                street = db.session.query(Street).filter_by(id=int(id))
                if street:
                    return street.first()
        except ValueError:
            return None
        return None

    @staticmethod
    #@cache.memoize()
    def getAllStreets(cityid=0):
        """
        Get all streets of city given by id, *0* for all streets

        :param optional cityid: id of city, *0* for all
        :return: list of :py:class:`emonitor.modules.streets.street.Street`
        """
        if cityid == 0:
            return db.session.query(Street).all()
        else:
            return db.session.query(Street).filter_by(cityid=cityid).all()
            
    @staticmethod
    def getStreetsDict():
        """
        Get dict of streets, id as key

        :return: cict of :py:class:`emonitor.modules.streets.street.Street`
        """
        ret = {}
        for street in db.session.query(Street).filter_by(active=1).order_by('name'):
            ret[street.id] = street
        ret[0] = Street('', '', 0, '', 0, 0, 0, 1, 0)
        return ret
