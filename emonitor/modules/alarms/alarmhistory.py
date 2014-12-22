import datetime
from emonitor.extensions import db


class AlarmHistory(db.Model):
    """AlarmHistory class user in :py:class:`emonitor.modules.alarms.alarm.Alarm`"""
    __tablename__ = 'alarmhistory'

    historytypes = ['autochangeState', 'message']

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DATETIME, default=datetime.datetime.now())
    name = db.Column(db.String(32))
    value = db.Column(db.Text)
    alarm_id = db.Column(db.Integer, db.ForeignKey('alarms.id'))

    def __repr__(self):
        return self.name

    def __init__(self, name, value, dtime):
        self.name = name
        self.value = value
        self.timestamp = dtime

    #@property
    #def history_key(self):
    #    return (self.timestamp, self.name)
