import yaml
from emonitor.extensions import db


class Housenumber(db.Model):
    __tablename__ = 'housenumbers'
    
    id = db.Column(db.Integer, primary_key=True)
    streetid = db.Column(db.Integer, db.ForeignKey('streets.id'))
    number = db.Column(db.String(10))
    _points = db.Column('points', db.Text)

    def __init__(self, streetid, number, points):
        self.streetid = streetid
        self.number = number
        self._points = points

    @property
    def points(self):
        return yaml.load(self._points)

    @staticmethod
    def getHousenumbers(id=0):
        if id == 0:
            return db.session.query(Housenumber).all()
        else:
            return db.session.query(Housenumber).filter_by(id=int(id)).first()

