from sqlalchemy.orm.collections import attribute_mapped_collection
from emonitor.extensions import db, classes
from emonitor.modules.monitors.monitorlayout import MonitorLayout


class Monitor(db.Model):
    __tablename__ = 'monitors'

    id = db.Column(db.Integer, primary_key=True)
    clientid = db.Column(db.Integer)
    name = db.Column(db.String(30))
    orientation = db.Column(db.Integer, default=0)
    resolutionx = db.Column(db.Integer, default=0)
    resolutiony = db.Column(db.Integer, default=0)
    formatx = db.Column(db.Integer, default=0)
    formaty = db.Column(db.Integer, default=0)
    
    layouts = db.relationship("MonitorLayout", collection_class=attribute_mapped_collection('id'), cascade="all, delete-orphan")

    def _get_current_layout(self):
        layoutid = 0
        
        def findid(clientid):
            for ml in classes.get('monitorlog').getLogForClient(clientid):
                if ml.type == 'change layout':
                    for p in ml.operation.split(';'):
                        
                        if p.startswith('layoutid='):
                            return int(p.replace('layoutid=', ''))

        layoutid = findid(self.clientid)
        #layouts = self.getLayouts()
        try:
            if layoutid > 0:
                return filter(lambda l: l.id == layoutid, self.layouts.values())[0]
            else:  # return defaultlayout
                return filter(lambda l: l.trigger == 'default', self.layouts.values())[0]
        except:
            ml = MonitorLayout(self.id, 'default', '--', '', 0, 0, 0)
            ml.theme = ml.themes[0]
            return ml
            
    currentlayout = property(_get_current_layout)

    def __repr__(self):
        return '<Monitor %r>' % self.clientid
    
    def __init__(self, clientid, name, orientation, resolutionx, resolutiony, formatx, formaty):
        self.clientid = clientid
        self.name = name
        self.orientation = orientation
        self.resolutionx = resolutionx
        self.resolutiony = resolutiony
        self.formatx = formatx
        self.formaty = formaty
        
    def layout(self, layoutid):
        l = db.session.query(MonitorLayout).filter_by(id=int(layoutid))
        if l.first():
            return l.first()
        else:  # deliver default layout
            return self.currentlayout
        
    def getLayouts(self, triggername=""):
        if triggername == "":
            return sorted(self.layouts.values())
        elif triggername != "":
            return filter(lambda x: x.trigger.startswith(triggername), sorted(self.layouts.values()))

    @staticmethod
    def getMonitors(id=0, clientid=0):
        if id != 0:
            return db.session.query(Monitor).filter_by(id=id).first()
        elif clientid != 0:
            return db.session.query(Monitor).filter_by(clientid=id).first()
        else:
            return db.session.query(Monitor).order_by('clientid').all()

    @staticmethod
    def handleEvent(eventname, *kwargs):
        return True
