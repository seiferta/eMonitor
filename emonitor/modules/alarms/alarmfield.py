import sys
import inspect
import yaml
from jinja2 import TemplateNotFound
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declared_attr
from flask import render_template
from emonitor.extensions import db, babel
from emonitor.modules.cars.car import Car


class FieldName(object):
    def __init__(self, label, id, prefix=u"ext", **args):
        self.name = label
        self.id = id
        self.prefix = prefix
        self.args = args

    def __repr__(self):
        return self.id

    def getLabel(self):
        ret = unicode(self.name)
        if ret.endswith('_'):
            ret = ret[:-1]
        if ret.startswith(' '):
            ret = ret.strip()
        if "labelprefix" in self.args:
            ret = u"{}{}".format(self.args['labelprefix'], ret)
        return ret

    def getName(self):
        return u'{}.{}'.format(self.prefix, self.id)

    def getValue(self, alarm, default=''):
        v = yaml.load(alarm.get(u'{}'.format(self.prefix))) or {}
        if self.id in v:
            return v[self.id]
        return default

    def getArg(self, name):
        """
        Get args of field
        :param name: special args: newline, child, freetext
        :return:
        """
        if name == "newline":
            return self.name.endswith('_')
        elif name == "child":
            return self.name.startswith(' ')
        elif name == "freetext":
            return self.name.strip().startswith('<') and self.name.strip().endswith('>')
        elif name in self.args:
            return self.args[name]
        return ""


class AlarmField(db.Model):
    __version__ = '0.1'

    __tablename__ = 'alarmfields'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    fieldtype = db.Column('type', db.String(32))
    name = db.Column(db.String(64))
    _parameters = db.Column('parameters', db.Text)
    dept = db.Column('dept', db.Integer, db.ForeignKey('departments.id'))
    position = db.Column(db.Integer)
    department = db.relationship("Department", collection_class=attribute_mapped_collection('id'))

    @property
    def hasEditForm(self):
        return True

    @declared_attr
    def __mapper_args__(self):
        return {'polymorphic_on': self.fieldtype, 'polymorphic_identity': self.__name__}

    def __init__(self, name, dept, parameters, position):
        self.fieldtype = self.__class__.__name__
        if self.fieldtype == name:  # translate if classname an name are same
            name = babel.gettext(name)
        self.name = name
        self.dept = dept
        self._parameters = yaml.safe_dump(parameters, encoding='utf-8')
        self.position = position

    def __repr__(self):
        return '{} - {}'.format(self.__class__.__name__, self.id)

    @property
    def parameters(self):
        return yaml.load(self._parameters)

    @parameters.setter
    def parameters(self, params):
        self._parameters = yaml.safe_dump(params, encoding='utf-8')

    def getFields(self, **params):
        return []

    def getFieldValue(self, fieldname, alarm):
        if fieldname.startswith('alarm.'):
            return ">>", alarm.get(fieldname.split('.')[1])  # TODO
        return None

    def getExportFields(self):
        return []

    def configForm(self, dept=0):
        return render_template('fields/field.config_{}.html'.format(self.fieldtype.lower()), field=self, dept=dept)

    def editForm(self, alarm):
        try:
            return render_template('fields/field.edit_{}.html'.format(self.fieldtype.lower()), field=self, alarm=alarm)
        except TemplateNotFound:
            return ""

    def saveForm(self, request, alarm):
        pass

    def renderField(self, alarm, **params):
        try:
            return render_template('fields/field.render_{}.html'.format(self.fieldtype.lower()), field=self, alarm=alarm, params=params)
        except:
            pass

    @staticmethod
    def getAlarmFields(id=0, dept=0, fieldtype=""):
        if id != 0:
            return AlarmField.query.filter_by(id=id).first()
        elif dept != 0:
            return AlarmField.query.filter(AlarmField.dept == dept).order_by('position').all()
        elif fieldtype != "":
            return AlarmField.query.filter(AlarmField.fieldtype == fieldtype).first()
        else:
            return AlarmField.query.order_by('name').all()

    @staticmethod
    def getAlarmFieldsDict():
        return dict(map(lambda x: [x.id, [x]], AlarmField.query.all()))

    @staticmethod
    def getAlarmFieldsForDepartment(dept):
        ret = []
        for field in AlarmField.getAlarmFields(dept=dept):
            ret.append(field)
        i = 0
        for name, cls in inspect.getmembers(sys.modules[__name__]):
            if inspect.isclass(cls) and len(cls.__bases__) > 0 and cls.__bases__[0].__name__ == 'AlarmField':
                if len(filter(lambda c: c.__class__.__name__ == name, ret)) == 0:
                    ret.append(cls(name, dept, [], i))
                    i += 1
        return ret

    @staticmethod
    def getAlarmFieldForType(fieldtype, dept=0):
        for name, cls in inspect.getmembers(sys.modules[__name__]):
            if inspect.isclass(cls) and cls.__name__ == fieldtype:
                position = 0
                dbFields = AlarmField.getAlarmFieldsDict()
                if int(dept) in dbFields.keys():
                    position = len(dbFields[int(dept)])
                return cls(cls.__name__, int(dept), {}, position)


class AFBasic:
    """
    deliver basic information for alarms
    """
    __version__ = '0.1'

    def __init__(self):
        pass

    def getFields(self, **params):
        return [FieldName('basic.address', babel.gettext('admin.alarms.address')),
                FieldName('basic.department', babel.gettext('admin.alarms.department')),
                FieldName('basic.department.address', babel.gettext('admin.alarms.department.address')),
                FieldName('basic.currentdate', babel.gettext('admin.currentdate')),
                FieldName('alarm.key', babel.gettext('alarms.key')),
                FieldName('alarm.date', babel.gettext('alarms.date')),
                FieldName('alarm.time', babel.gettext('alarms.time'))]

    def getFieldValue(self, fieldname, alarm):
        if fieldname == "basic.address":
            return "%s, %s %s" % (alarm.city.name, alarm.street.name, alarm.housenumber.number)
        elif fieldname == "basic.department":
            if alarm.getDepartment().address_name != "":
                return "%s" % alarm.getDepartment().address_name
            return "%s" % alarm.getDepartment().name
        elif fieldname == "basic.department.address":
            return "%s - %s - %s" % (alarm.getDepartment().address_name, alarm.getDepartment().address_street, alarm.getDepartment().address_city)
        elif fieldname == "basic.currentdate":
            return "NOW()"
        else:
            return fieldname.encode('utf-8')


class AFTime(AlarmField):
    __version__ = '0.1'

    def getFields(self, **params):
        return [FieldName('alarmtime{}'.format(field), 'alarmtime{}'.format(field), prefix=u"", labelprefix='alarms.') for field in range(1, 5)] + [FieldName('alarmend', 'alarmend', prefix=u'', labelprefix='alarms.')]

    def getFieldValue(self, fieldname, alarm):
        return alarm.get(fieldname).encode('utf-8')

    def getExportFields(self):
        return [('alarms.alarmtime', 'alarmtime'), ('alarms.time_3', 'alarmtime3'), ('alarms.time_4', 'alarmtime4'), ('alarms.time_1', 'alarmtime1'), ('alarms.time_2', 'alarmtime2'), ('alarms.alarmend', 'alarmend')]

    def saveForm(self, request, alarm):
        for field in range(1, 5):  # alarmtime1-4
            alarm.set('alarmtime{}'.format(field), request.form.get('alarmtime{}'.format(field)))
        alarm.set('alarmend', request.form.get('alarmend'))


class AFAlerting(AlarmField):
    __version__ = '0.1'

    def getFields(self, **params):
        return [FieldName(field[0], field[1], prefix=u"ext.afalerting") for field in self.parameters]

    def getExportFields(self):
        ret = []
        l = 0
        for f in self.getFields():
            if f.getArg('child'):
                l += 1
                if l == 1:
                    ret[-1] = ("{} ({})".format(ret[-1][0], babel.gettext('list')), ret[-1][1])
            else:
                l = 0
                ret.append((f.getLabel(), f.id))
        return ret

    def saveConfigForm(self, request):
        _names = request.form.getlist(u'alerting.field.name')
        _values = request.form.getlist(u'alerting.field.value')
        if _names[-1] == _values[-1] == u'':
            _names = _names[:-1]
            _values = _values[:-1]
        self.parameters = zip(_names, _values)

    def saveForm(self, request, alarm):
        """
        save parameters for alerting field

        :param request: request with all form parameters
        :param alarm: alarm object
        """
        params = {}
        for field in self.getFields():
            if request.form.get(field.getName()) is not None:
                params[field.getName().split('.')[-1]] = request.form.get(field.getName())
            elif field.getName() in request.form.getlist(u'ext.afalerting'):
                params[field.getName().split('.')[-1]] = True
        alarm.set('ext.afalerting', yaml.safe_dump(params, encoding='utf-8'))


class AFCars(AlarmField):
    __version__ = '0.1'

    @property
    def hasEditForm(self):
        return False

    def getFields(self, **params):
        """
        get list of fields = list of active cars
        :param params: dept for department-filter
        :return:
        """
        if 'dept' in params:
            cars = [c for c in Car.getCars(deptid=params['dept'].id) if c.active]
        else:
            cars = [c for c in Car.getCars() if c.active]
        return [FieldName(car.name, u'{}'.format(car.id), prefix=u"") for car in cars]

    def getFieldValue(self, fieldname, alarm):
        """
        return formated value for cars of given alarm

        :param fieldname:
        :param alarm: alarm class
        :return: string
        """
        if fieldname == 'list':
            return ", ".join([c.name.encode('utf-8') for c in alarm.cars1])

    def getExportFields(self):
        return [('cars (list)', 'cars')]


class AFPersons(AlarmField):
    __version__ = '0.1'

    def getFields(self, **params):
        _names = ['sum', 'alarm', 'house_', 'pa', 'pa_alarm', 'pa_house_', 'el']  # 'elgrade' + 'style'
        f = map(lambda z: (FieldName(z, z, prefix=u'ext.afpersons', fieldtype='checkbox', active=list(filter(lambda x: x[0] == z, self.parameters) or [[z, z, 'false']])[0][2], labelprefix='alarms.fields.persons.field.')), _names)
        f.append(FieldName('elgrade', 'elgrade', prefix=u'ext.afpersons', fieldtype='list', listvalues=['LM', 'BM', 'sonst'], active=list(filter(lambda x: x[0] == 'elgrade', self.parameters) or [['elgrade', 'elgrade', 'false']])[0][2], labelprefix='alarms.fields.persons.field.'))
        f.append(FieldName('style', 'style', prefix=u'ext.afpersons', fieldtype='radio', listvalues=['simple', 'extended'], active=list(filter(lambda x: x[0] == 'style', self.parameters) or [['style', 'style', 'false']])[0][2], labelprefix='alarms.fields.persons.field.'))
        return f

    def getFieldValue(self, fieldname, alarm):
        vals = yaml.load(alarm.get('ext.afpersons'))
        if vals:
            if fieldname in vals:
                return vals[fieldname]
        return ""

    def saveConfigForm(self, request):
        params = {}
        for field in self.getFields():
            if field.getArg('fieldtype') in ['checkbox', 'list']:  # for checkbox type
                if field.getName() in request.form:
                    params[field.getName().split('.')[-1]] = 'true'
                else:
                    params[field.getName().split('.')[-1]] = 'false'
            #elif field.getArg('fieldtype') == 'list' and field.getName() in request.form:  # for list type
            #    params[field.getName().split('.')[-1]] = request.form.get(field.getName())
            elif field.getArg('fieldtype') == 'radio' and field.getName() in request.form:  # for radio type
                params[field.getName().split('.')[-1]] = request.form.get(field.getName())
        self.parameters = zip(params.keys(), params.keys(), params.values())

    def saveForm(self, request, alarm):
        """
        save parameters for persons field

        :param request: request with all form parameters
        :param alarm: alarm object
        """
        params = {}
        for field in self.getFields():
            if request.form.get(field.getName()) is not None:
                params[field.getName().split('.')[-1]] = request.form.get(field.getName())
            elif field.getName() in request.form.getlist(u'ext.afalerting'):
                params[field.getName().split('.')[-1]] = True
        alarm.set('ext.afpersons', yaml.safe_dump(params, encoding='utf-8'))


class AFMaterial(AlarmField):
    __version__ = '0.1'

    def getFields(self, **params):
        return [FieldName(field[0], field[1], prefix=u"ext.afmaterial", check=field[2]) for field in self.parameters]

    def getFieldValue(self, fieldname, alarm):
        fields = self.getFields()
        vals = yaml.load(alarm.get('ext.afmaterial'))
        if vals and fieldname.endswith('list'):  # deliver list of all used material
            ret = []
            for k, v in vals.iteritems():
                if filter(lambda x: x.id == k, fields)[0]:
                    item = filter(lambda x: x.id == k, fields)[0]
                    if 'check' in item.args and item.args['check'] == 'true':
                        ret.append(u'{}x {}'.format(v, item.getLabel()))
                    else:
                        ret.append(u'{}'.format(item.getLabel()))
            return ", ".join(ret)
        elif not vals:
            return ""
        else:
            return fieldname

    def saveConfigForm(self, request):
        _names = request.form.getlist(u'material.field.name')
        _values = request.form.getlist(u'material.field.value')
        _check = request.form.getlist(u'material.field.check')
        if _names[-1] == _values[-1] == '':
            _names = _names[:-1]
            _values = _values[:-1]
            _check = _check[:-1]
        self.parameters = zip(_names, _values, _check)

    def saveForm(self, request, alarm):
        params = {}
        for field in self.getFields():
            if request.form.get('ext.afmaterial.{}'.format(field.id), '') != '':
                params[field.id] = request.form.get('ext.afmaterial.{}'.format(field.id), '')
        alarm.set('ext.afmaterial', yaml.safe_dump(params, encoding='utf-8'))


class AFOthers(AlarmField):
    __version__ = '0.1'

    def getFields(self, **params):
        return [FieldName(field[0], field[1], prefix=u"ext.afothers", check=field[2]) for field in self.parameters]

    def saveConfigForm(self, request):
        _names = request.form.getlist(u'others.field.name')
        _values = request.form.getlist(u'others.field.value')
        _check = request.form.getlist(u'others.field.check')
        if _names[-1] == _values[-1] == '':
            _names = _names[:-1]
            _values = _values[:-1]
            _check = _check[:-1]
        map(lambda x: x.encode('utf-8'), _names)
        self.parameters = zip(_names, _values, _check)


class AFDamage(AlarmField):
    __version__ = '0.1'


class AFReport(AlarmField):
    __version__ = '0.1'

    def getFields(self, **params):
        return [FieldName(babel.gettext('AFReport'), 'report', prefix=u'ext.afreport')]

    def getFieldValue(self, fieldname, alarm):
        vals = yaml.load(alarm.get('ext.afreport'))
        if vals:
            if fieldname in vals:
                return vals[fieldname]
            return "; ".join(vals.values())
        else:
            return u""

    def saveForm(self, request, alarm):
        """
        save parameters for report field

        :param request: request with all form parameters
        :param alarm: alarm object
        """
        params = {}
        for field in self.getFields():
            if request.form.get(field.getName()) is not None:
                params[field.getName().split('.')[-1]] = request.form.get(field.getName())
        alarm.set('ext.afreport', yaml.safe_dump(params, encoding='utf-8'))
