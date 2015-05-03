from sqlalchemy.orm.collections import attribute_mapped_collection
from emonitor.extensions import db
from emonitor.modules.monitors.monitorlayout import MonitorLayout
from emonitor.widget.monitorwidget import MonitorWidget


class Monitor(db.Model):
    """Monitor class"""
    __tablename__ = 'monitors'
    __table_args__ = {'extend_existing': True}

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
        from emonitor.monitorserver import MonitorLog
        layoutid = 0
        
        def findid(clientid):
            for ml in MonitorLog.getLogForClient(clientid):
                if ml.type == 'change layout':
                    for p in ml.operation.split(';'):
                        
                        if p.startswith('layoutid='):
                            return int(p.replace('layoutid=', ''))

        layoutid = findid(self.clientid)
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
        """
        Get MonitorLayout for given id
        :param layoutid: id as integer
        :return: :py:class:`emonitor.modules.monitors.monitorlayout.MonitorLayout`
        """
        l = MonitorLayout.getLayouts(id=int(layoutid))
        if l:
            return l
        else:  # deliver default layout
            return self.currentlayout
        
    def getLayouts(self, triggername=""):
        """
        Get list of all MonitorLayouts defined for *triggername* or all
        :param optional triggername: triggername as filter
        :return: list of :py:class:`emonitor.modules.monitors.monitorlayout.MonitorLayout`
        """
        if triggername == "":
            return sorted(self.layouts.values())
        elif triggername != "":
            return filter(lambda x: x.trigger.startswith(triggername), sorted(self.layouts.values()))

    @staticmethod
    def getMonitors(id=0, clientid=0):
        """
        Get list of monitor definitions filtered by parameters

        :param optional id:
        :param optional clientid:
        :return: list of :py:class:`emonitor.modules.monitors.monitor.Monitor`
        """
        if id != 0:
            return Monitor.query.filter_by(id=id).first()
        elif clientid != 0:
            return Monitor.query.filter_by(clientid=clientid).first()
        else:
            return Monitor.query.order_by('clientid').all()

    @staticmethod
    def handleEvent(eventname, **kwargs):
        return kwargs


class PlaceholderWidget(MonitorWidget):
    """Placeholder widget for monitors"""
    template = 'widget.placeholder.html'
    size = (1, 1)

    def addParameters(self, **kwargs):
        self.params.update(kwargs)
