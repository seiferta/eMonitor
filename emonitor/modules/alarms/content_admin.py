import os
import imp
from flask import render_template, request, current_app

from emonitor.extensions import db, classes, scheduler, babel
from .alarmutils import AlarmFaxChecker, processFile


def getAdminContent(self, **params):
    module = request.view_args['module'].split('/')

    if len(module) > 1:
        if module[1] == 'types':
            impl = []  # load implementations of faxchecker
            for f in [f for f in os.listdir('%s/emonitor/modules/alarms/inc/' % current_app.config.get('PROJECT_ROOT')) if f.endswith('.py')]:
                if not f.startswith('__'):
                    cls = imp.load_source('emonitor.modules.alarms.inc', 'emonitor/modules/alarms/inc/%s' % f)
                    if isinstance(getattr(cls, cls.__all__[0])(), AlarmFaxChecker):
                        impl.append((f, getattr(cls, cls.__all__[0])(), classes.get('alarmtype').getAlarmTypeByClassname(f)))

            if request.method == 'POST':
                if request.form.get('action') == 'createtype':  # add type
                    params.update({'alarmtype': classes.get('alarmtype')('', ''), 'interpreter': impl})
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
                    params.update({'alarmtype': classes.get('alarmtype').getAlarmTypes(id=int(request.form.get('action').split('_')[-1])), 'interpreter': impl})
                    return render_template('admin.alarms.type_actions.html', **params)

                elif request.form.get('action').startswith('deletetype_'):  # delete type
                    db.session.delete(classes.get('alarmtype').getAlarmTypes(id=int(request.form.get('action').split('_')[-1])))
                    db.session.commit()

                elif request.form.get('action') == 'updatetype':  # update type
                    if request.form.get('type_id') == 'None':  # add type
                        atype = classes.get('alarmtype')('', '')
                        db.session.add(atype)
                    else:  # update
                        atype = classes.get('alarmtype').getAlarmTypes(id=int(request.form.get('type_id')))

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
                                db.session.add(classes.get('alarmsection')(atype.id, key, sections[key][0], 1, sections[key][1], i))
                                i += 1
                        db.session.commit()

                elif request.form.get('action').startswith('createsection_'):  # add section
                    alarmtype = classes.get('alarmtype').getAlarmTypes(id=int(request.form.get('action').split('_')[-1]))
                    params.update({'alarmtype': alarmtype, 'section': classes.get('alarmsection')(alarmtype.id, '', '', 0, '', 0), 'functions': alarmtype.interpreterclass().getEvalMethods()})
                    return render_template('admin.alarms.sections_actions.html', **params)

                elif request.form.get('action') == 'updatesection':  # save section
                    if request.form.get('section_id') == 'None':  # add
                        section = classes.get('alarmsection')('', '', '', '', '', '')
                        db.session.add(section)
                        section.orderpos = 1 + len(classes.get('alarmsection').getSections())

                    else:  # update
                        section = classes.get('alarmsection').getSections(id=int(request.form.get('section_id')))
                        section.orderpos = request.form.get('edit_orderpos')

                    section.tid = request.form.get('edit_tid')
                    section.name = request.form.get('edit_name')
                    section.key = request.form.get('edit_key')
                    section.method = request.form.get('edit_method')
                    section.active = request.form.get('edit_active')
                    db.session.commit()

                elif request.form.get('action').startswith('editalarmsection_'):  # edit section
                    section = classes.get('alarmsection').getSections(id=int(request.form.get('action').split('_')[-1]))
                    params.update({'section': section, 'functions': section.alarmtype.interpreterclass().getEvalMethods(), 'alarmtype': classes.get('alarmtype').getAlarmTypes(section.tid)})
                    return render_template('admin.alarms.sections_actions.html', **params)

                elif request.form.get('action').startswith('deletealarmsection_'):  # delete section
                    section = classes.get('alarmsection').getSections(id=int(request.form.get('action').split('_')[-1]))
                    db.session.delete(section)
                    db.session.commit()

            params.update({'alarmtypes': classes.get('alarmtype').getAlarmTypes(), 'interpreters': impl})
            return render_template('admin.alarms.type.html', **params)

        elif module[1] == 'test':
            return render_template('admin.alarms.test.html', **params)

    else:
        alarms = classes.get('alarm').getAlarms()
        stats = dict.fromkeys(classes.get('alarm').ALARMSTATES.keys() + ['3'], int(0))
        for alarm in alarms:
            stats[str(alarm.state)] += 1
        params.update({'alarms': alarms, 'stats': stats, 'alarmstates': classes.get('alarm').ALARMSTATES})
        return render_template('admin.alarms.html', **params)


def getAdminData(self):

    if request.args.get('action') == 'upload':
        if request.files:
            ufile = request.files['uploadfile']
            fname = os.path.join(current_app.config.get('PATH_TMP'), ufile.filename)
            ufile.save(fname)

            scheduler.add_single_job(processFile, [current_app.config.get('PATH_TMP'), ufile.filename])  # schedule operation
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
