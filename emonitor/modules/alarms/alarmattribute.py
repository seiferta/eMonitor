from emonitor.extensions import db


class AlarmAttribute(db.Model):
    """AlarmAttribute class, used in :py:class:`emonitor.modules.alarms.alarm.Alarm`"""
    __tablename__ = 'alarmattributes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    value = db.Column(db.Text)
    alarm_id = db.Column(db.Integer, db.ForeignKey('alarms.id'))

    def __repr__(self):
        return self.name

    def __init__(self, name, value):
        self.name = name
        self.value = value
