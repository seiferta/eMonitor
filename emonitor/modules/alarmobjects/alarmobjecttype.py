from sqlalchemy.sql import collate
from emonitor.extensions import db


class AlarmObjectType(db.Model):
    __tablename__ = 'alarmobjecttypes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    remark = db.Column(db.Text)

    def __init__(self, name, remark):
        self.name = name
        self.remark = remark

    @staticmethod
    def getAlarmObjectTypes(id=0):
        if id != 0:
            return db.session.query(AlarmObjectType).filter_by(id=id).first()
        else:
            return db.session.query(AlarmObjectType).order_by(collate(AlarmObjectType.name, 'NOCASE')).all()
