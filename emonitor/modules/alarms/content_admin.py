import os
import imp
import random
from emonitor.lib.pdf.pdf import getFormFields, getPDFInformation
from flask import render_template, request, current_app

from emonitor.extensions import db, scheduler, babel
from emonitor.modules.alarms.alarmutils import AlarmFaxChecker, processFile
from emonitor.modules.alarms.alarm import Alarm
from emonitor.modules.alarms.alarmfield import AlarmField
from emonitor.modules.alarms.alarmtype import AlarmType
from emonitor.modules.alarms.alarmsection import AlarmSection
from emonitor.modules.alarms.alarmreport import AlarmReport
from emonitor.modules.settings.settings import Settings
from emonitor.modules.settings.department import Department
from emonitor.modules.cars.car import Car


def getAdminContent(self, **params):
    """
    Deliver admin content of module alarms

    :param params: use given parameters of request
    :return: rendered template as string
    """
    module = request.view_args['module'].split('/')

    if len(module) > 1:
        if module[1] == 'types':
            impl = []  # load implementations of faxchecker
            for f in [f for f in os.listdir('%s/emonitor/modules/alarms/inc/' % current_app.config.get('PROJECT_ROOT')) if f.endswith('.py')]:
                if not f.startswith('__'):
                    cls = imp.load_source('emonitor.modules.alarms.inc', 'emonitor/modules/alarms/inc/%s' % f)
                    if isinstance(getattr(cls, cls.__all__[0])(), AlarmFaxChecker):
                        impl.append((f, getattr(cls, cls.__all__[0])(), AlarmType.getAlarmTypeByClassname(f)))

            if request.method == 'POST':
                if request.form.get('action') == 'createtype':  # add type
                    params.update({'alarmtype': AlarmType('', ''), 'interpreter': impl})
                    return render_template('admin.alarms.type_actions.html', **params)

                elif request.form.get('action').startswith('deleteinterpreter_'):  # delete checker
                    for cls in impl:
                        if cls[0] == request.form.get('action')[18:]:
                            if os.path.exists('%s/emonitor/modules/alarms/inc/%s' % (current_app.config.get('PROJECT_ROOT'), cls[0])):
                                os.remove('%s/emonitor/modules/alarms/inc/%s' % (current_app.config.get('PROJECT_ROOT'), cls[0]))
                            if os.path.exists('%s/emonitor/modules/alarms/inc/%sc' % (current_app.config.get('PROJECT_ROOT'), cls[0])):
                                os.remove('%s/emonitor/modules/alarms/inc/%sc' % (current_app.config.get('PROJECT_ROOT'), cls[0]))
                            impl.remove(cls)

                elif request.form.get('action').startswith('editalarmtype_'):  # edit type
                    params.update({'alarmtype': AlarmType.getAlarmTypes(id=int(request.form.get('action').split('_')[-1])), 'interpreter': impl})
                    return render_template('admin.alarms.type_actions.html', **params)

                elif request.form.get('action').startswith('deletetype_'):  # delete type
                    db.session.delete(AlarmType.getAlarmTypes(id=int(request.form.get('action').split('_')[-1])))
                    db.session.commit()

                elif request.form.get('action') == 'updatetype':  # update type
                    if request.form.get('type_id') == 'None':  # add type
                        atype = AlarmType('', '')
                        db.session.add(atype)
                    else:  # update
                        atype = AlarmType.getAlarmTypes(id=int(request.form.get('type_id')))

                    atype.name = request.form.get('edit_name')
                    atype.keywords = request.form.get('edit_keywords')
                    atype.interpreter = request.form.get('edit_interpreter')
                    translations = dict()
                    _vars = request.form.getlist('alarmtypevariables')
                    _values = request.form.getlist('alarmtypetranslation')
                    for _var in _vars:
                        translations[_var] = _values[_vars.index(_var)]
                    atype.translations = translations
                    db.session.commit()

                    if request.form.get('type_id') == 'None':  # add predefined keywords and sections
                        # add pre-defined sections
                        for checker in [i for i in impl if i[0] == request.form.get('edit_interpreter')]:
                            if request.form.get('edit_keywords') == "":
                                atype.keywords = "\n".join(checker[1].getDefaultConfig()['keywords'])
                            sections = checker[1].getDefaultConfig()['sections']
                            i = 1
                            for key in sections:
                                db.session.add(AlarmSection(atype.id, key, sections[key][0], 1, sections[key][1], i))
                                i += 1
                        db.session.commit()

                elif request.form.get('action').startswith('createsection_'):  # add section
                    alarmtype = AlarmType.getAlarmTypes(id=int(request.form.get('action').split('_')[-1]))
                    params.update({'alarmtype': alarmtype, 'section': AlarmSection(alarmtype.id, '', '', 0, '', 0), 'functions': alarmtype.interpreterclass().getEvalMethods()})
                    return render_template('admin.alarms.sections_actions.html', **params)

                elif request.form.get('action') == 'updatesection':  # save section
                    if request.form.get('section_id') == 'None':  # add
                        section = AlarmSection('', '', '', '', '', '')
                        db.session.add(section)
                        section.orderpos = 1 + len(AlarmSection.getSections())

                    else:  # update
                        section = AlarmSection.getSections(id=int(request.form.get('section_id')))
                        section.orderpos = request.form.get('edit_orderpos')

                    section.tid = request.form.get('edit_tid')
                    section.name = request.form.get('edit_name')
                    section.key = request.form.get('edit_key')
                    section.method = request.form.get('edit_method')
                    section.active = request.form.get('edit_active')
                    db.session.commit()

                elif request.form.get('action').startswith('editalarmsection_'):  # edit section
                    section = AlarmSection.getSections(id=int(request.form.get('action').split('_')[-1]))
                    params.update({'section': section, 'functions': section.alarmtype.interpreterclass().getEvalMethods(), 'alarmtype': AlarmType.getAlarmTypes(section.tid)})
                    return render_template('admin.alarms.sections_actions.html', **params)

                elif request.form.get('action').startswith('deletealarmsection_'):  # delete section
                    section = AlarmSection.getSections(id=int(request.form.get('action').split('_')[-1]))
                    db.session.delete(section)
                    db.session.commit()

            params.update({'alarmtypes': AlarmType.getAlarmTypes(), 'interpreters': impl})
            return render_template('admin.alarms.type.html', **params)

        elif module[1] == 'report':

            if request.method == 'POST':
                if request.form.get('action') == 'createreport':  # add report
                    params.update({'report': AlarmReport('', '', '', 1, []), 'departments': Department.getDepartments(), 'reporttypes': AlarmReport.getReportTypes()})
                    return render_template('admin.alarms.report_action.html', **params)

                elif request.form.get('action') == 'updatereport':
                    if request.form.get('report_id') == 'None':  # add new report
                        report = AlarmReport('', '', '', '')
                        db.session.add(report)
                    else:
                        report = AlarmReport.getReports(request.form.get('report_id'))

                    report.name = request.form.get('edit_name')
                    if not request.form.get('template').startswith(current_app.config.get('PATH_DATA')):  # internal template
                        report._reporttype = 'internal'
                        report.filename = request.form.get('template').replace("{}/emonitor/modules/alarms/templates/".format(current_app.config.get('PROJECT_ROOT')).replace('\\', '/'), "")
                    else:
                        report._reporttype = 'external'
                        report.filename = request.form.get('template').replace("{}".format(current_app.config.get('PATH_DATA')), "")
                    report.departments = request.form.getlist('edit_department')
                    db.session.commit()

                elif request.form.get('action').startswith('editreport_'):  # edit report
                    report = AlarmReport.getReports(request.form.get('action').split('_')[-1])
                    params.update({'report': report, 'departments': Department.getDepartments(), 'reporttypes': AlarmReport.getReportTypes()})
                    return render_template('admin.alarms.report_action.html', **params)

                elif request.form.get('action').startswith('deletereport_'):  # delete report
                    report = AlarmReport.getReports(request.form.get('action').split('_')[-1])
                    if AlarmReport.query.filter(AlarmReport.filename == report.filename).count() == 1 and os.path.exists(report.filename):
                        os.remove(report.filename)
                    db.session.delete(report)
                    db.session.commit()

            params.update({'reports': AlarmReport.getReports(), 'departments': Department.getDepartments()})
            return render_template('admin.alarms.report.html', **params)

        elif module[1] == 'config':
            if request.method == 'POST':
                if request.form.get('action') == 'alarmcarsprio':
                    for k in Alarm.ALARMSTATES.keys():
                        if 'used_cars{}'.format(k) in request.form.keys():
                            Settings.set('alarms.spc_cars.{}'.format(k), request.form.get('used_cars{}'.format(k)))
                    db.session.commit()

                elif request.form.get('action') == 'alarmsettings':
                    Settings.set('alarms.autoclose', request.form.get('settings.autoclose'))
                    for aalarm in [a for a in Alarm.getAlarms() if a.state == 1]:  # only active alarms
                        aalarm.updateSchedules(reference=1)  # use alarmtime as refernce

                elif request.form.get('action') == 'archivesettings':
                    Settings.set('alarms.autoarchive', request.form.get('settings.autoarchive'))
                    for aalarm in [a for a in Alarm.getAlarms() if a.state == 2]:  # only closed alarms
                        aalarm.updateSchedules(reference=1)  # use alarmtime as refernce

                elif request.form.get('action').startswith('save_'):
                    if request.form.get('fieldid') == 'None':
                        field = AlarmField.getAlarmFieldForType(request.form.get('action').split('_')[1], dept=request.form.get('action').split('_')[2])
                        db.session.add(field)
                    else:
                        field = AlarmField.getAlarmFields(id=request.form.get('fieldid'))
                    field.saveConfigForm(request)
                    db.session.commit()

                elif request.form.get('action').startswith('field_delete_'):  # delete definition of field
                    db.session.delete(AlarmField.getAlarmFields(id=request.form.get('action').split('_')[-1]))
                    db.session.commit()

                elif request.form.get('action').startswith('field_add_'):  # add field for department
                    field = AlarmField.getAlarmFieldForType(request.form.get('action').split('_')[-2], dept=request.form.get('action').split('_')[-1])
                    field.name = babel.gettext(field.name)
                    db.session.add(field)
                    db.session.commit()

            fields = {}
            for dept in Department.getDepartments():
                fields[dept.id] = AlarmField.getAlarmFieldsForDepartment(dept.id)
            params.update({'cars': Car.getCars(), 'alarmstates': Alarm.ALARMSTATES, 'settings': Settings, 'departments': Department.getDepartments(), 'fields': fields})
            return render_template('admin.alarms.config.html', **params)

        elif module[1] == 'test':
            params.update({'uploadfileformat': filter(None, sum([Settings.get('ocr.inputformat', []), Settings.get('ocr.inputtextformat', [])], []))})
            return render_template('admin.alarms.test.html', **params)

    else:
        params.update({'alarms': dict(Alarm.getAlarmCount()), 'alarmstates': Alarm.ALARMSTATES, 'help': self.hasHelp('admin')})
        return render_template('admin.alarms.html', **params)


def getAdminData(self):
    """
    Deliver admin content of module alarms (ajax)

    :return: rendered template as string or json dict
    """
    if request.args.get('action') == 'upload':
        if request.files:
            ufile = request.files['uploadfile']
            fname = os.path.join(current_app.config.get('PATH_TMP'), ufile.filename)
            ufile.save(fname)

            scheduler.add_job(processFile, args=[current_app.config.get('PATH_TMP'), ufile.filename])  # schedule operation
        return ""

    elif request.args.get('action') == 'uploadchecker':
        if request.files:
            ufile = request.files['uploadfile']
            if not os.path.exists('%s/emonitor/modules/alarms/inc/%s' % (current_app.config.get('PROJECT_ROOT'), ufile.filename)):
                ufile.save('%s/emonitor/modules/alarms/inc/%s' % (current_app.config.get('PROJECT_ROOT'), ufile.filename))
                try:
                    cls = imp.load_source('emonitor.modules.alarms.inc', 'emonitor/modules/alarms/inc/%s' % ufile.filename)
                    if isinstance(getattr(cls, cls.__all__[0])(), AlarmFaxChecker):
                        return "ok"
                except:
                    pass
                os.remove('%s/emonitor/modules/alarms/inc/%s' % (current_app.config.get('PROJECT_ROOT'), ufile.filename))
                return babel.gettext(u'admin.alarms.checkernotvalid')
        return ""

    elif request.args.get('action') == 'getkeywords':
        for f in [f for f in os.listdir('%s/emonitor/modules/alarms/inc/' % current_app.config.get('PROJECT_ROOT')) if f.endswith('.py')]:
            if f == request.args.get('checker'):
                cls = imp.load_source('emonitor.modules.alarms.inc', 'emonitor/modules/alarms/inc/%s' % f)
                variables = getattr(cls, cls.__all__[0])().getDefaultConfig()[u'translations']
                return {u'keywords': "\n".join(getattr(cls, cls.__all__[0])().getDefaultConfig()[u'keywords']), u'variables': variables}
        return ""

    elif request.args.get('action') == 'alarmsforstate':
        alarms = Alarm.getAlarms(state=int(request.args.get('state')))
        return render_template('admin.alarms_alarm.html', alarms=alarms)

    elif request.args.get('action') == 'alarmsarchive':
        for id in request.args.get('alarmids').split(','):
            Alarm.changeState(int(id), 3)
        return ""

    elif request.args.get('action') == 'savefieldorder':  # change order of fields
        fields = []
        deptid = '0'
        for f in request.args.get('order').split(','):
            t, deptid, name = f.split('.')
            fields.append(name)
        if int(deptid):
            for dbfield in AlarmField.getAlarmFields(dept=deptid):
                dbfield.position = fields.index(dbfield.fieldtype)
            db.session.commit()
        return ""

    elif request.args.get('action') == 'addreport':
        f = request.files['template']
        fname = "{}.{}".format(random.random(), f.filename.split('.')[-1])
        fpath = '{}alarmreports/{}'.format(current_app.config.get('PATH_DATA'), fname[2:])
        f.save(fpath)

        if f.filename.endswith('pdf'):
            fields = getFormFields(fpath)
            content = render_template('admin.alarms.report_fields.html', filepath='{}alarmreports/{}'.format(current_app.config.get('PATH_DATA'), fname[2:]), fileinfo=getPDFInformation(fpath), fields=fields, multi=max(fields.values()) > 1)
        else:
            fields = []
        return {'filename': fname, 'content': content}
