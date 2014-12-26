import os
from flask import request, render_template, current_app, redirect
from emonitor.modules.settings.settings import Settings

from emonitor.extensions import alembic, classes, db, babel

OBSERVERACTIVE = 1


def getAdminContent(self, **params):
    """
    Deliver admin content of module settings

    :param params: use given parameters of request
    :return: rendered template as string
    """
    module = request.view_args['module'].split('/')

    def chunks(l, n):
        return [l[i:i + n] for i in range(0, len(l), n)]

    if len(module) == 2:
        if module[1] == 'department':  # department submodule
            if request.method == 'POST':
                if request.form.get('action') == 'savedept':  # save department
                    if request.form.get('dep_id') != 'None':  # update
                        department = classes.get('department').getDepartments(request.form.get('dep_id'))
                        l = request.form.get('dep_pos')
                    else:  # add
                        l = len(classes.get('department').getDepartments()) + 1
                        department = classes.get('department')('', '', '', 0)
                        db.session.add(department)
                    department.name = request.form.get('dep_name')
                    department.shortname = request.form.get('dep_shortname')
                    department.color = request.form.get('dep_color')
                    department.orderpos = l
                    department.defaultcity = request.form.get('dep_city')
                    db.session.commit()
                    
                elif request.form.get('action') == 'createdepartment':  # add department
                    params.update({'department': classes.get('department')('', '', '', 0)})
                    return render_template('admin.settings.department_actions.html', **params)

                elif request.form.get('action').startswith('detaildept_'):  # edit department
                    params.update({'department': classes.get('department').getDepartments(request.form.get('action').split('_')[-1]), 'cities': classes.get('city').getCities()})
                    return render_template('admin.settings.department_actions.html', **params)

                elif request.form.get('action').startswith('deletedept_'):  # delete department
                    db.session.delete(classes.get('department').getDepartments(int(request.form.get('action').split('_')[-1])))
                    db.session.commit()
                    
                elif request.form.get('action') == 'ordersetting':  # change department order
                    for _id in request.form.getlist('departmentids'):
                        classes.get('department').getDepartments(int(_id)).orderpos = request.form.getlist('departmentids').index(_id) + 1
                    db.session.commit()
            
            params.update({'departments': classes.get('department').getDepartments(), 'cities': classes.get('city').getCities()})
            return render_template('admin.settings.department.html', **params)

        elif module[1] == 'cars':
            if request.method == 'POST':
                if request.form.get('action') == 'updatetypes':
                    cartypes = Settings.get_byType('cartypes')
                    if not cartypes:  # add cartype
                        cartypes = Settings.get('cartypes', [])
                        db.session.add(cartypes)

                    cartypes.value = [i for i in chunks(request.form.getlist('cartype'), 2) if i[0] != '']
                    db.session.commit()
            params.update({'cartypes': classes.get('settings').getCarTypes()})
            return render_template('admin.settings.cars.html', **params)

        elif module[1] == 'start':

            if request.method == 'POST':
                if request.form.get('action') == 'updatestart':  # update start page definition
                    areas = dict()
                    areas['center'] = {'module': request.form.get('center.module'), 'width': '0', 'visible': 1}
                    areas['west'] = {'module': request.form.get('west.module'), 'moduleadd': request.form.getlist('west.module.add'), 'width': '.%s' % request.form.get('west.width'), 'visible': request.form.get('west.visible')}
                    areas['east'] = {'module': request.form.get('east.module'), 'moduleadd': request.form.getlist('east.module.add'), 'width': '.%s' % request.form.get('east.width'), 'visible': request.form.get('east.visible')}

                    Settings.set('frontend.default', areas)
                    db.session.commit()

            def modname(obj):  # get translation for sorting of module
                _t = "module.%s" % obj.info['name']
                return babel.gettext(_t)

            params.update({'mods': sorted([m for m in current_app.blueprints['frontend'].modules.values() if m.frontendContent() == 1], key=modname), 'center': classes.get('settings').getFrontendSettings('center'), 'west': classes.get('settings').getFrontendSettings('west'), 'east': classes.get('settings').getFrontendSettings('east')})
            return render_template('admin.settings.start.html', **params)

    else:

        if request.method == 'POST':  # save settings
            if request.form.get('action') == 'observerstate':
                classes.get('settings').set('obeserver.active', request.form.get('observerstate'))
            elif request.form.get('action') == 'alarmsettings':
                classes.get('settings').set('alarms.autoclose', request.form.get('settings.autoclose'))
            elif request.form.get('action') == 'archivesettings':
                classes.get('settings').set('alarms.autoarchive', request.form.get('settings.autoarchive'))

        paths = dict(pathdata=current_app.config.get('PATH_DATA'), pathtmp=current_app.config.get('PATH_TMP'), pathincome=current_app.config.get('PATH_INCOME'), pathdone=current_app.config.get('PATH_DONE'))

        params.update({'paths': paths, 'observerstate': OBSERVERACTIVE, 'alarmsettings': classes.get('settings').get('alarms.autoclose'), 'archivesettings': classes.get('settings').get('alarms.autoarchive'), 'alarmsevalfields': classes.get('settings').get('alarms.evalfields'), 'alembic': alembic})
        return render_template('admin.settings.html', **params)
    return redirect("/admin/settings", code=302)


def getAdminData(self, **params):
    """
    Deliver admin content of module settings (ajax)

    :return: rendered template as string or json dict
    """
    if request.args.get('action') == 'checkpath':
        if os.path.exists(request.args.get('path')):
            return '1'
        return '0'

    elif request.args.get('action') == 'upgradedb':
        try:
            alembic.upgrade()
            return str(alembic.current())
        except:
            return babel.gettext(u'admin.settings.updatedberror')

    elif request.args.get('action') == 'downgradedb':
        return alembic.downgrade() or "done"

    return ""
