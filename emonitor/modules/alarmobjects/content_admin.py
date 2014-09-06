from flask import render_template, request
from emonitor.extensions import classes, db


def getAdminContent(self, **params):
    streets = classes.get('street').getAllStreets()
    
    if request.method == 'POST':
        if request.form.get('action') == 'createalarmobject':  # add alarmobject
            params.update({'alarmobject': classes.get('alarmobject')('', 0, '', classes.get('settings').get('defaultLat'), classes.get('settings').get('defaultLng'), classes.get('settings').get('defaultZoom'), '', ''), 'streets': streets, 'selectedstreet': '', 'map': classes.get('map').getDefaultMap()})
            return render_template('admin.alarmobjects_actions.html', **params)

        elif request.form.get('action') == 'savealarmobject':  # save
            if request.form.get('alarmobject_id') == 'None':  # add new
                alarmobject = classes.get('alarmobject')('', 0, '', 0, 0, 0, '', '')
                db.session.add(alarmobject)
            else:  # update existing
                alarmobject = classes.get('alarmobject').getAlarmObjects(id=request.form.get('alarmobject_id'))
            alarmobject.name = request.form.get('edit_name')
            alarmobject.streetid = request.form.get('streetid')
            alarmobject.remark = request.form.get('edit_remark')
            if request.form.get('edit_position') == '1':
                alarmobject.lat = request.form.get('edit_lat')
                alarmobject.lng = request.form.get('edit_lng')
                alarmobject.zoom = request.form.get('edit_zoom')
            alarmobject.streetno = request.form.get('edit_streetno')
            alarmobject.alarmplan = request.form.get('edit_alarmplan')

            db.session.commit()
            
        elif request.form.get('action').startswith('editalarmobject_'):  # edit alarmobject
            alarmobject = classes.get('alarmobject').getAlarmObjects(id=int(request.form.get('action').split('_')[-1]))
            params.update({'alarmobject': alarmobject, 'streets': streets, 'selectedstreet': '%s (%s)' % (alarmobject.street.name, alarmobject.street.city.name), 'map': classes.get('map').getDefaultMap()})
            return render_template('admin.alarmobjects_actions.html', **params)

        elif request.form.get('action').startswith('deletealarmobject_'):  # delete alarmobject
            db.session.delete(classes.get('alarmobject').getAlarmObjects(id=int(request.form.get('action').split('_')[-1])))
            db.session.commit()
    
    params.update({'alarmobjects': classes.get('alarmobject').getAlarmObjects()})
    return render_template('admin.alarmobjects.html', **params)

    
def getAdminData(self, params={}):
    
    return ""