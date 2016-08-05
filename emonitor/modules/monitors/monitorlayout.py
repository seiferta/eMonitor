import os
import yaml
from PIL import Image, ImageDraw
from math import ceil
from flask import current_app
from sqlalchemy.orm import relationship
from StringIO import StringIO

from emonitor.extensions import db
#from emonitor.modules.monitors.monitor import Monitor


class MonitorLayout(db.Model):
    """MonitorLayout class"""
    __tablename__ = 'monitorlayouts'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    mid = db.Column(db.Integer, db.ForeignKey('monitors.id'))
    trigger = db.Column(db.TEXT, default='default')
    _layout = db.Column('layout', db.Text)
    theme = db.Column(db.String(30))
    mintime = db.Column(db.Integer, default=0)
    maxtime = db.Column(db.Integer, default=0)
    nextid = db.Column(db.Integer, default=0)

    monitor = relationship("Monitor", backref="monitors", lazy='joined')

    @property
    def layout(self):
        """
        Use yaml for layout

        :return: yaml formated data
        """
        return yaml.load(self._layout)

    @layout.setter
    def layout(self, val):
        """
        Setter for layout

        :param val: value list with parameters for widgets
        """
        l = []
        for item in val:
            if len(item.split(';')) == 5:
                i = item.split(';')
                l.append(dict(widget=i[0], width=int(i[1]), height=int(i[2]), col=int(i[3]), row=int(i[4])))
        self._layout = yaml.safe_dump(l, encoding='utf-8')

    #@property
    #def monitor(self):
    #    """Build monitor from mid"""
    #    return Monitor.getMonitors(id=self.mid)

    def _get_themes(self):
        ret = []
        for root, dirs, files in os.walk("%s/emonitor/frontend/web/css" % current_app.config.get('PROJECT_ROOT')):
            for name in [f for f in files if f.startswith('monitor_')]:
                ret.append(name.split('_')[1][:-4])
        return ret
    themes = property(_get_themes)

    def _get_html_layout(self):
        """
        Build default html layout for widget configuration

        :return: html string with layout areas for widget content
        """
        ret = ""
        items, max_x, max_y = MonitorLayout._evalLayout(self.layout)
        for l in items:
            _l = str(int(ceil((l['startx'] - 1) * (100.0 / max_x)))) + '%'
            _t = str(int(ceil((l['starty'] - 1) * (100.0 / max_y)))) + '%'
            _r = str(100 - int(ceil((l['endx']) * (100.0 / max_x)))) + '%'
            _b = str(100 - int(ceil((l['endy']) * (100.0 / max_y)))) + '%'
            ret += '<div id="area" style="position:fixed;left:%s;top:%s;right:%s;bottom:%s;">[[%s]]</div>\n' % (_l, _t, _r, _b, l['widget'])
        return ret

    htmllayout = property(_get_html_layout)

    def __repr__(self):
        return "monitorlayout"

    def __init__(self, mid, trigger, layout, theme, mintime, maxtime, nextid):
        self.mid = mid
        self.trigger = trigger
        self.layout = layout
        self.theme = theme
        self.mintime = mintime
        self.maxtime = maxtime
        self.nextid = nextid

    @staticmethod
    def _evalLayout(text):
        ret = []
        max_x = max_y = 1
        if text is None:
            return [dict(startx=1, starty=1, endx=1, endy=1, name='placeholder')], 1, 1
        for l in text:
            ret.append(dict(startx=l['col'], starty=l['row'], endx=(l['width'] + l['col'] - 1), endy=(l['height'] + l['row'] - 1), widget=l['widget']))
            if l['width'] + l['col'] - 1 > max_x:
                max_x = l['width'] + l['col'] - 1
            if l['height'] + l['row'] - 1 > max_y:
                max_y = l['height'] + l['row'] - 1
        return ret, max_x, max_y

    def getHTMLLayoutScript(self):
        ret = '$(function(){'
        for l in self.layout:
            try:
                ret += 'addWidget("%s", %s, %s, %s, %s);\n' % (l['widget'], l['width'], l['height'], l['col'], l['row'])
            except:
                pass
        return ret + '});'

    def getLayoutThumb(self):
        """
        Calculate the thumbnail of the layout on-the-fly

        :return: stream of image file
        """
        dimension = (12, 9)
        ret, max_x, max_y = MonitorLayout._evalLayout(self.layout)

        img = Image.new('RGB', (max_x * dimension[0] + 1, max_y * dimension[1] + 1), (171, 171, 171))
        draw = ImageDraw.Draw(img)
        for l in ret:
            draw.rectangle([((l['startx'] - 1) * dimension[0], (l['starty'] - 1) * dimension[1]),
                            ((l['endx']) * dimension[0], (l['endy']) * dimension[1])], fill="white", outline='black')
        output = StringIO()
        img.save(output, format="PNG", dpi=(300, 300))
        return output.getvalue()

    @staticmethod
    def getLayouts(id=0, mid=0):
        """
        Get list of layout definitions filtered by parameters

        :param optional id: filter only layout with id, *0* for all layouts
        :param optional mid: monitorid as integer
        :return: list of :py:class:`emonitor.modules.monitors.monitorlyout.MonitorLayout`
        """
        if id != 0:
            return MonitorLayout.query.filter_by(id=id).first()
        elif mid != 0:
            return MonitorLayout.query.filter_by(mid=mid).all()
        else:
            return MonitorLayout.query.order_by('mid').all()

    def getTriggerNames(self):
        return self.trigger.split(';')
