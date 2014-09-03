from sqlalchemy.orm.collections import attribute_mapped_collection
from emonitor.extensions import db, cache


class City(db.Model):
    __tablename__ = 'cities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    dept = db.Column('dept', db.Integer, db.ForeignKey('departments.id'))
    mapname = db.Column(db.String(30))
    default = db.Column(db.Integer)
    subcity = db.Column(db.Text)
    color = db.Column(db.String(6), default="000000")
    osmid = db.Column(db.Integer, default=0)
    osmname = db.Column(db.String(30), default="")
    
    streets = db.relationship("Street", collection_class=attribute_mapped_collection('id'), cascade="all, delete-orphan")
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
    
    def getSubCityList(self):
        try:
            return [s for s in self.subcity.split("\r\n") if s.strip() != ""]
        except:
            return []

    def getSubCityListLine(self):
        try:
            return ", ".join([s for s in self.subcity.split("\r\n") if s.strip() != ""])
        except:
            return ""
    
    def getColorName(self):
        return '#%s' % self.color
        
    def __repr__(self):
        return '<City %r>' % self.name
        
    @cache.memoize()
    def getStreets(self):
        return sorted(self.streets.values(), key=lambda x: x.name)
        
    def addStreet(self, street):
        #cache.delete_memoized('getStreets', self)
        if street.id in self.streets:
            self.streets[street.id] = street
        else:
            self.streets[street.id] = street
        db.session.commit()
    
    # static part
    @staticmethod
    def getCities():
        return db.session.query(City).order_by(City.default.desc(), City.name).all()
        
    @staticmethod
    def getCitiesDict():
        ret = {}
        for city in db.session.query(City).order_by('id'):
            ret[city.id] = city
            if city.default == 1:
                ret[0] = city
        return ret
        
    @staticmethod
    def get_byid(cityid):
        return db.session.query(City).filter_by(id=cityid).first() or None
        
    @staticmethod
    def get_byname(cityname):
        city = db.session.query(City).filter_by(name=cityname).first()
        #if city[0]:
        #    return city[0]
        #return None
        return city or None
        
    @staticmethod
    def getDefaultCity():
        city = db.session.query(City).filter_by(default=1).first()
        return city or None
        #if city.first():
        #    return city.first()
        #else:
        #    return None
