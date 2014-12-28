import os
import random
from flask import render_template, request, current_app
from emonitor.extensions import classes, db


def getAdminContent(self, **params):
    """
    Deliver admin content of module alarmobjects

    :param params: use given parameters of request
    :return: rendered template as string
    """
    module = request.view_args['module'].split('/')

    def chunks(l, n):
        return [l[i:i + n] for i in range(0, len(l), n)]

    if len(module) > 1:  # type definition
        if module[1] == 'types':
            if request.method == 'POST':
                if request.form.get('action') == 'createalarmobjecttype':  # add type
                    params.update({'alarmobjecttype': classes.get('alarmobjecttype')('', '')})
                    return render_template('admin.alarmobjects.types_action.html', **params)

                elif request.form.get('action') == 'savealarmobjecttype':  # save type
                    if request.form.get('alarmobjecttype_id') == 'None':  # add new type
                        alarmobjecttype = classes.get('alarmobjecttype')('', '')
                        db.session.add(alarmobjecttype)
                    else:  # update existing
                        alarmobjecttype = classes.get('alarmobjecttype').getAlarmObjectTypes(id=int(request.form.get('alarmobjecttype_id')))
                    alarmobjecttype.name = request.form.get('alarmobjecttype_name')
                    alarmobjecttype.remark = request.form.get('alarmobjecttype_remark')
                    db.session.commit()

                elif request.form.get('action').startswith('detailobjecttype'):  # edit type
                    alarmobjecttype = classes.get('alarmobjecttype').getAlarmObjectTypes(id=int(request.form.get('action').split('_')[-1]))
                    params.update({'alarmobjecttype': alarmobjecttype})
                    return render_template('admin.alarmobjects.types_action.html', **params)

                elif request.form.get('action').startswith('deleteobjecttype_'):  # delete type
                    db.session.delete(classes.get('alarmobjecttype').getAlarmObjectTypes(id=int(request.form.get('action').split('_')[-1])))
                    db.session.commit()

            params.update({'alarmobjecttypes': classes.get('alarmobjecttype').getAlarmObjectTypes()})
            return render_template('admin.alarmobjects.types.html', **params)

        elif module[1] == 'fields':
            if request.method == 'POST':
                if request.form.get('action') == 'updatefield':  # update fields
                    classes.get('settings').set('alarmobjectfields', [i for i in chunks(request.form.getlist('fieldname'), 2) if i[0] != ''])
                    db.session.commit()

            params.update({'fields': classes.get('settings').get('alarmobjectfields', [])})
            return render_template('admin.alarmobjects.fields.html', **params)

    else:  # base view
        if request.method == 'POST':
            streets = classes.get('street').getAllStreets()
            if request.form.get('action') == 'createalarmobject':  # add alarmobject
                params.update({'alarmobject': classes.get('alarmobject')('', 0, '', classes.get('settings').get('defaultLat'), classes.get('settings').get('defaultLng'), classes.get('settings').get('defaultZoom'), '', '', '', 0, 0), 'streets': streets, 'selectedstreet': '', 'map': classes.get('map').getDefaultMap(), 'alarmobjecttypes': classes.get('alarmobjecttype').getAlarmObjectTypes()})
                return render_template('admin.alarmobjects_actions.html', **params)

            elif request.form.get('action') == 'savealarmobject':  # save
                if request.form.get('alarmobject_id') == 'None':  # add new
                    alarmobject = classes.get('alarmobject')('', 0, '', 0, 0, 0, '', '', '', 0, 0)
                    db.session.add(alarmobject)
                else:  # update existing
                    alarmobject = classes.get('alarmobject').getAlarmObjects(id=request.form.get('alarmobject_id'))
                alarmobject.name = request.form.get('edit_name')
                alarmobject._streetid = request.form.get('streetid')
                alarmobject._objecttype = int(request.form.get('edit_objecttype'))
                alarmobject.remark = request.form.get('edit_remark')
                if request.form.get('edit_position') == '1':
                    alarmobject.lat = request.form.get('edit_lat')
                    alarmobject.lng = request.form.get('edit_lng')
                    alarmobject.zoom = request.form.get('edit_zoom')
                alarmobject.streetno = request.form.get('edit_streetno')
                alarmobject.alarmplan = request.form.get('edit_alarmplan')
                alarmobject.bma = request.form.get('edit_bma')
                alarmobject.active = int(request.form.get('edit_active', '0'))
                db.session.commit()

            elif request.form.get('action') == 'savealarmobjectattributes':  # save attributes
                alarmobject = classes.get('alarmobject').getAlarmObjects(id=request.form.get('alarmobject_id'))
                for field in classes.get('settings').get('alarmobjectfields', []):  # store attributes
                    if 'edit_%s' % field[0] in request.form:
                        alarmobject.set(field[0], request.form.get('edit_%s' % field[0]))
                db.session.commit()

            elif request.form.get('action') == 'savealarmobjectaao':  # save aao
                alarmobject = classes.get('alarmobject').getAlarmObjects(id=request.form.get('alarmobject_id'))
                alarmobject.set('cars1', request.form.get('cars1').split(';'))
                alarmobject.set('cars2', request.form.get('cars2').split(';'))
                alarmobject.set('material', request.form.get('material').split(';'))
                db.session.commit()

            elif request.form.get('action').startswith('editalarmobject_'):  # edit alarmobject
                alarmobject = classes.get('alarmobject').getAlarmObjects(id=int(request.form.get('action').split('_')[-1]))
                params.update({'alarmobject': alarmobject, 'streets': streets, 'selectedstreet': '%s (%s)' % (alarmobject.street.name, alarmobject.street.city.name), 'map': classes.get('map').getDefaultMap(), 'alarmobjecttypes': classes.get('alarmobjecttype').getAlarmObjectTypes(), 'fields': classes.get('settings').get('alarmobjectfields', []), 'cars': classes.get('car').getCars(deptid=classes.get('department').getDefaultDepartment().id)})
                return render_template('admin.alarmobjects_actions.html', **params)

            elif request.form.get('action').startswith('deletealarmobject_'):  # delete alarmobject
                db.session.delete(classes.get('alarmobject').getAlarmObjects(id=int(request.form.get('action').split('_')[-1])))
                db.session.commit()

        params.update({'alarmobjects': classes.get('alarmobject').getAlarmObjects(active=0), 'alarmobjecttypes': classes.get('alarmobjecttype').getAlarmObjectTypes()})
        return render_template('admin.alarmobjects.html', **params)

    
def getAdminData(self):
    """
    Deliver admin content of module alarmobjects (ajax)

    :return: rendered template as string or json dict
    """
    if request.args.get('action') == 'uploadfile':  # add file for alarmobject
        ufile = request.files['uploadfile']
        filetype = request.form.get('name')
        alarmobject = classes.get('alarmobject').getAlarmObjects(id=request.form.get('alarmobject_id'))
        filename = '%s%s' % (str(random.random())[2:], os.path.splitext(ufile.filename)[1])

        if not os.path.exists('%salarmobjects/%s/' % (current_app.config.get('PATH_DATA'), alarmobject.id)):  # create base directory
            os.makedirs('%salarmobjects/%s/' % (current_app.config.get('PATH_DATA'), alarmobject.id))

        ufile.save('%salarmobjects/%s/%s' % (current_app.config.get('PATH_DATA'), alarmobject.id, filename))
        alarmobject.files.set(classes.get('alarmobjectfile')(alarmobject.id, filename, filetype))
        db.session.commit()
        return render_template('admin.alarmobjects.file.html', alarmobject=alarmobject)

    elif request.args.get('action') == 'deletefile':  # delete file with id
        objectfile = classes.get('alarmobjectfile').getFile(id=request.args.get('id'))
        oid = objectfile.object_id
        if os.path.exists('%salarmobjects/%s/%s' % (current_app.config.get('PATH_DATA'), oid, objectfile.filename)):
            os.remove('%salarmobjects/%s/%s' % (current_app.config.get('PATH_DATA'), oid, objectfile.filename))
        db.session.delete(objectfile)
        db.session.commit()
        alarmobject = classes.get('alarmobject').getAlarmObjects(id=oid)
        return render_template('admin.alarmobjects.file.html', alarmobject=alarmobject)

    return ""
