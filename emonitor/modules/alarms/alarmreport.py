import os
import re
import glob
import codecs
import json
from flask import render_template, current_app
from emonitor.extensions import db, babel
from emonitor.lib.pdf.pdf import getPDFInformation, getFormFields

reporttitle = re.compile(r'(.*)title>(?P<reportname>(.*))</title(.*)')


class AlarmReportType:

    def __init__(self, filename, rtype="internal"):
        self.filename = filename
        if os.path.exists(filename):
            # try html
            if filename.endswith('html'):
                m = reporttitle.match(re.sub(' |\r|\n', '', codecs.open(filename, 'r', encoding="utf-8").read()))
                if m:
                    self.name = m.groupdict()['reportname']
                else:
                    self.name = "<unnamed>"
                self.multi = 'multi' in filename
            # try pdf
            if filename.endswith('pdf'):
                info = getPDFInformation(filename)
                self.name = u"{} - {}".format(info['title'], info['author'])
                fields = getFormFields(filename)
                self.multi = max(fields.values()) > 1

        else:
            self.name = ""
        self.type = rtype

    def __str__(self):
        return u'{} ({})'.format(self.name, babel.gettext(self.type))


class AlarmReport(db.Model):

    __tablename__ = 'alarmreports'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    filename = db.Column(db.TEXT)
    _reporttype = db.Column('reporttype', db.String(32))
    _fields = db.Column('fields', db.Text)
    _dept = db.Column('dept', db.String(32))

    def __init__(self, name, filename, reporttype, dept, fields=[]):
        self.name = name
        self.filename = filename
        self._reporttype = reporttype
        self._dept = dept
        self._fields = json.dumps(fields)

    @property
    def fields(self):
        return []

    @property
    def departments(self):
        try:
            return [int(m) for m in self._dept.split(',')]
        except ValueError:
            return []

    @departments.setter
    def departments(self, departments):
        self._dept = ','.join(departments)

    @property
    def reporttype(self):
        if self._reporttype == 'internal':
            fname = "{}/emonitor/modules/alarms/templates/{}".format(current_app.config.get('PROJECT_ROOT'), self.filename)
        else:
            fname = "{}{}".format(current_app.config.get('PATH_DATA'), self.filename)
        return AlarmReportType(fname.replace('\\', '/'), rtype=self._reporttype)

    def getHTML(self, **params):
        return render_template('reports/{}'.format(self.filename), **params)

    @staticmethod
    def getReportTypes():
        from emonitor import app
        ret = [AlarmReportType(f.replace('\\', '/')) for f in glob.glob('{}/emonitor/modules/alarms/templates/report.*.html'.format(app.config.get('PROJECT_ROOT')))]
        ret.extend([AlarmReportType(f.replace('\\', '/'), rtype="external") for f in glob.glob('{}alarmreports/*.*'.format(app.config.get('PATH_DATA')))])
        return ret

    @staticmethod
    def getReports(id=0):
        if id == 0:
            return AlarmReport.query.all()
        else:
            return AlarmReport.query.filter_by(id=id).first()
