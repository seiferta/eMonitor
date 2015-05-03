from sqlalchemy.orm.collections import attribute_mapped_collection
from emonitor.extensions import db, cache
from emonitor.modules.streets.street import Street


class City(db.Model):
    """City class"""
    __tablename__ = 'cities'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    dept = db.Column('dept', db.Integer, db.ForeignKey('departments.id'))
    mapname = db.Column(db.String(30))
    default = db.Column(db.Integer)
    subcity = db.Column(db.Text)
    color = db.Column(db.String(6), default="000000")
    osmid = db.Column(db.Integer, default=0)
    osmname = db.Column(db.String(30), default="")
    
    streets = db.relationship("Street", collection_class=attribute_mapped_collection('id'), backref=db.backref('City', remote_side=[Street.cityid]), cascade="all, delete-orphan")
    department = db.relationship("Department", collection_class=attribute_mapped_collection('id'))
    
    def __init__(self, name, dept, mapname, default, subcity, color, osmid, osmname):
        self.name = name
        self.dept = dept
        self.mapname = mapname
        self.default = default
        self.subcity = subcity
        self.color = color
        self.osmid = osmid
        self.osmname = osmname

    @property
    def serialize(self):
        return dict(id=self.id, name=self.name)

    @property
    def subcities(self):
        return filter(None, self.subcity.split("\r\n"))

    def getColorName(self):
        return '#%s' % self.color
        
    def __repr__(self):
        return '<City %r>' % self.name

    def addStreet(self, street):
        """
        Add street to current city

        :param street: :py:class:`emonitor.modules.streeets.street.Street`
        """
        #cache.delete_memoized('getStreets', self)
        if street.id in self.streets:
            self.streets[street.id] = street
        else:
            self.streets[street.id] = street
        db.session.commit()
    
    # static part
    @staticmethod
    def getCities(id=0):
        """
        Get list of all cities

        :return: list of :py:class:`emonitor.modules.streets.city.City`
        """
        if id == 0:
            return City.query.order_by(City.default.desc(), City.name).all()
        else:
            return City.query.filter_by(id=id).first()

    @staticmethod
    def getCitiesDict():
        """
        Get cities as dict

        :return: dict of :py:class:`emonitor.modules.streets.city.City`, id as key
        """
        ret = dict(db.get(City.id, City).order_by(City.id))
        ret[0] = City.getDefaultCity()
        return ret

    @staticmethod
    def getDefaultCity():
        """
        Get default city (default=1)

        :return: :py:class:`emonitor.modules.streets.city.City`
        """
        return City.query.filter_by(default=1).first()
