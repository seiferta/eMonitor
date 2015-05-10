from sqlalchemy.sql import collate
from emonitor.extensions import db


class AlarmObjectType(db.Model):
    """Type definition for AlarmObjects"""
    __tablename__ = 'alarmobjecttypes'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    remark = db.Column(db.Text)

    def __init__(self, name, remark):
        self.name = name
        self.remark = remark

    @staticmethod
    def getAlarmObjectTypes(id=0):
        """
        Get list of AlarmObjectTypes

        :param id: id of :py:mod:`emonitor.modules.alarmobjects.alarmobjecttype.AlarmObjectType`
        :return: list or single :py:mod:`emonitor.modules.alarmobjects.alarmobjecttype.AlarmObjectType`
        """
        if id != 0:
            return AlarmObjectType.query.filter_by(id=id).first()
        else:
            try:
                return AlarmObjectType.query.order_by(collate(AlarmObjectType.name, 'NOCASE')).all()
            except:
                return AlarmObjectType.query.order_by(AlarmObjectType.name).all()
