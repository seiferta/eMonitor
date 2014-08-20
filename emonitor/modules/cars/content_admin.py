from flask import request, render_template
from emonitor.extensions import db, classes


def getAdminContent(self, **params):
    module = request.view_args['module'].split('/')
    
    if len(module) < 2:
        module.append(u'1')
        
    if request.method == 'POST':
        if request.form.get('action') == 'createcars':  # add car
            params.update({'car': classes.get('car')('', '', '', '', '', int(module[1])), 'departments': classes.get('department').getDepartments(), 'cartypes': classes.get('settings').getCarTypes()})
            return render_template('admin.cars_edit.html', **params)

        elif request.form.get('action') == 'updatecars':  # save car
            if request.form.get('car_id') != 'None':  # update car
                car = classes.get('car').getCars(id=request.form.get('car_id'))
                
            else:  # add car
                car = classes.get('car')('', '', '', '', '', module[1])
                db.session.add(car)

            car.name = request.form.get('edit_name')
            car.description = request.form.get('edit_description')
            car.fmsid = request.form.get('edit_fmsid')
            car.active = request.form.get('edit_active')
            car.type = request.form.get('edit_type')
            car._dept = request.form.get('edit_department')
            db.session.commit()
            
        elif request.form.get('action') == 'cancel':
            pass
            
        elif request.form.get('action').startswith('editcars_'):  # edit car
            params.update({'car': classes.get('car').getCars(id=request.form.get('action').split('_')[-1]), 'departments': classes.get('department').getDepartments(), 'cartypes': classes.get('settings').getCarTypes()})
            return render_template('admin.cars_edit.html', **params)

        elif request.form.get('action').startswith('deletecars_'):  # delete car
            db.session.delete(classes.get('car').getCars(id=request.form.get('action').split('_')[-1]))
            db.session.commit()
    try:
        params.update({'cars': classes.get('department').getDepartments(module[1]).getCars()})
    except AttributeError:
        params.update({'cars': []})
    return render_template('admin.cars.html', **params)
