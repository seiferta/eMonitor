import os
from flask import current_app
from sqlalchemy.sql import collate
from emonitor.extensions import db


class AlarmObjectFile(db.Model):
    __tablename__ = 'alarmobjectfile'

    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer, db.ForeignKey('alarmobjects.id'))
    filename = db.Column(db.String(80))
    filetype = db.Column(db.String(50))

    def __repr__(self):
        return "<alarmobjectfile %s>" % self.filename

    def __init__(self, objectid, filename, filetype):
        self.object_id = objectid
        self.filename = filename
        self.filetype = filetype

    @property
    def filesize(self):
        def sizeof_fmt(num):
            for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
                if num < 1024.0:
                    return "%3.1f %s" % (num, x)
                num /= 1024.0
        if os.path.exists('%salarmobjects/%s/%s' % (current_app.config.get('PATH_DATA'), self.object_id, self.filename)):
            return sizeof_fmt(os.stat('%salarmobjects/%s/%s' % (current_app.config.get('PATH_DATA'), self.object_id, self.filename)).st_size)
        return sizeof_fmt(0)

    @staticmethod
    def getFile(id, filename=""):
        if filename == "":
            return db.session.query(AlarmObjectFile).filter_by(id=id).first()
        else:
            return db.session.query(AlarmObjectFile).filter_by(object_id=id, filename=filename).first()

    @staticmethod
    def getAlarmObjectTypes(objectid=0):
        if id != 0:
            return db.session.query(AlarmObjectFile).filter_by(id=id).all()
        else:
            return db.session.query(AlarmObjectFile).order_by(collate(AlarmObjectFile.name, 'NOCASE')).all()