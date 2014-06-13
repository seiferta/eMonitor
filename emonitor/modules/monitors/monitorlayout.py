import os
from PIL import Image, ImageDraw
from math import ceil
from flask import current_app

from emonitor.extensions import db


class MonitorLayout(db.Model):
    __tablename__ = 'monitorlayouts'

    id = db.Column(db.Integer, primary_key=True)
    mid = db.Column(db.Integer, db.ForeignKey('monitors.id'))
    trigger = db.Column(db.String(30), default='default')
    layout = db.Column(db.Text)
    theme = db.Column(db.String(30))
    mintime = db.Column(db.Integer, default=0)
    maxtime = db.Column(db.Integer, default=0)
    nextid = db.Column(db.Integer, default=0)

    def _get_themes(self):
        ret = []
        for root, dirs, files in os.walk("%s/emonitor/frontend/web/css" % current_app.config.get('PROJECT_ROOT')):
            for name in [f for f in files if f.startswith('monitor_')]:
                ret.append(name.split('_')[1][:-4])
        return ret
    themes = property(_get_themes)

    def _get_html_layout(self):
        ret = ""
        items, max_x, max_y = self._evalLayout(self.layout)
        for l in items:
            _l = str(int(ceil((l[0] - 1) * (100.0 / max_x)))) + '%'
            _t = str(int(ceil((l[1] - 1) * (100.0 / max_y)))) + '%'
            _r = str(100 - int(ceil((l[2]) * (100.0 / max_x)))) + '%'
            _b = str(100 - int(ceil((l[3]) * (100.0 / max_y)))) + '%'
            ret += '<div id="area" style="position:fixed;left:%s;top:%s;right:%s;bottom:%s;">[[%s]]</div>\n' % (_l, _t, _r, _b, l[-1])
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

    def _evalLayout(self, text):
        ret = []
        max_x = max_y = 1
        if text is None:
            return [[1, 1, 1, 1, 'placeholder']], 1, 1
        for l in text.split("\r\n")[:-1]:
            n = l.split(";")
            ret.append([int(n[3]), int(n[4]), (int(n[1]) + int(n[3]) - 1), (int(n[2]) + int(n[4]) - 1), n[0]])  # startx, starty, endx, endy, widgetname
            if int(n[1]) + int(n[3]) - 1 > max_x:
                max_x = int(n[1]) + int(n[3]) - 1
            if int(n[2]) + int(n[4]) - 1 > max_y:
                max_y = int(n[2]) + int(n[4]) - 1
        return ret, max_x, max_y

    def getHTMLLayoutScript(self):  # todo
        ret = '$(function(){'
        for l in self.layout.split("\r\n")[:-1]:
            try:
                n, x, y, c, r = l.split(";")
                ret += 'addWidget("%s", %s, %s, %s, %s);\n' % (n, x, y, c, r)
            except:
                pass
        return ret + '});'

    def getLayoutThumb(self):
        import StringIO

        dimension = (12, 9)
        ret, max_x, max_y = self._evalLayout(self.layout)

        img = Image.new('RGB', (max_x * dimension[0] + 1, max_y * dimension[1] + 1), (171, 171, 171))
        draw = ImageDraw.Draw(img)
        for l in ret:
            draw.rectangle([((l[0] - 1) * dimension[0], (l[1] - 1) * dimension[1]),
                            ((l[2]) * dimension[0], (l[3]) * dimension[1])], fill="white", outline='black')

        output = StringIO.StringIO()
        img.save(output, 'PNG')
        contents = output.getvalue()
        output.close()
        return contents

    @staticmethod
    def getLayouts(id=0, mid=0):
        if id != 0:
            return db.session.query(MonitorLayout).filter_by(id=id).first()
        elif mid != 0:
            return db.session.query(MonitorLayout).filter_by(mid=mid).all()
        else:
            return db.session.query(MonitorLayout).order_by('mid').all()


def _evalLayout(text):
    ret = []
    max_x = max_y = 1
    if not text:
        return [[1, 1, 1, 1, 'placeholder']], 1, 1
    for l in text.split("\r\n")[:-1]:
        n = l.split(";")
        ret.append([int(n[3]), int(n[4]), (int(n[1]) + int(n[3]) - 1), (int(n[2]) + int(n[4]) - 1), n[0]])  # startx, starty, endx, endy, widgetname
        if int(n[1]) + int(n[3]) - 1 > max_x:
            max_x = int(n[1]) + int(n[3]) - 1
        if int(n[2]) + int(n[4]) - 1 > max_y:
            max_y = int(n[2]) + int(n[4]) - 1
    return ret, max_x, max_y


def _get_themes():
    ret = []
    for root, dirs, files in os.walk("%s/emonitor/frontend/web/css" % current_app.config.get('PROJECT_ROOT')):
        for name in [f for f in files if f.startswith('monitor_')]:
            ret.append(name.split('_')[1][:-4])
    return ret
