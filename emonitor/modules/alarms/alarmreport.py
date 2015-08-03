import os
import re
import glob
import codecs
import yaml
import json
from flask import render_template, current_app
from emonitor.extensions import db, babel
from emonitor.modules.alarms.alarm import Alarm

reporttitle = re.compile(r'(.*)title>(?P<reportname>(.*))</title(.*)')


class AlarmReportType:

    def __init__(self, filename, rtype="internal"):
        self.filename = filename
        self._report = None
        if os.path.exists(filename):
            # try html
            if filename.endswith('html'):
                m = reporttitle.match(re.sub(' |\r|\n', '', codecs.open(filename, 'r', encoding="utf-8").read()))
                if m:
                    self.name = m.groupdict()['reportname']
                else:
                    self.name = "<unnamed>"
            # try pdf
            if filename.endswith('pdf'):
                from emonitor.lib.pdf.pdf import PDFFormFile
                self._report = PDFFormFile(self.filename)
                self.name = u"{} - {}".format(self._report.information['title'], self._report.information['author'])
        else:
            self.name = ""
        self.type = rtype

    @property
    def multi(self):
        if self._report:
            return self._report.multi
        return False

    @property
    def fields(self):
        if self._report:
            return self._report.fields
        return {}

    def createReport(self, alarms, fields):
        return self._report.createReport(alarmlist=[Alarm.getAlarms(id=alarm) for alarm in alarms], fielddefinition=fields)

    def __str__(self):
        return u'{} ({})'.format(self.name, babel.gettext(self.type))


class AlarmReport(db.Model):
    """
    alarm report class for database definition
    """

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
        self._fields = yaml.safe_dump(fields)

    @property
    def fields(self):
        """
        load field definition from database
        :return:
        """
        return yaml.load(self._fields)

    @fields.setter
    def fields(self, fields):
        """
        save fields in yaml format in database
        :param fields:
        :return:
        """
        self._fields = yaml.safe_dump(fields)

    def getFieldsJson(self):
        """
        defliver field definition in json format for web-forms
        :return:
        """
        return json.dumps(self.fields)

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

    def createReport(self, **kwargs):
        if 'ids' in kwargs:
            return self.reporttype.createReport(kwargs['ids'], self.fields)

    @staticmethod
    def getReportTypes(filename=""):
        from emonitor import app
        ret = [AlarmReportType(f.replace('\\', '/')) for f in glob.glob('{}/emonitor/modules/alarms/templates/report.*.html'.format(app.config.get('PROJECT_ROOT')))]
        ret.extend([AlarmReportType(f.replace('\\', '/'), rtype="external") for f in glob.glob('{}alarmreports/*.*'.format(app.config.get('PATH_DATA')))])

        if filename != "":  # filter elements
            return filter(lambda x: x.filename == filename, ret)[0]
        return ret

    @staticmethod
    def getReports(id=0):
        if id == 0:
            return AlarmReport.query.all()
        else:
            return AlarmReport.query.filter_by(id=id).first()
