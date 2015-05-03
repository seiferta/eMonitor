from flask import request, render_template
from emonitor.extensions import db
from emonitor.modules.settings.department import Department
from emonitor.modules.settings.settings import Settings
from emonitor.modules.cars.car import Car


def getAdminContent(self, **params):
    """
    Deliver admin content of module cars

    :param params: use given parameters of request
    :return: rendered template as string
    """
    module = request.view_args['module'].split('/')
    
    if len(module) < 2:
        module.append(u'1')
        
    if request.method == 'POST':
        if request.form.get('action') == 'createcars':  # add car
            params.update({'car': Car('', '', '', '', '', int(module[1])), 'departments': Department.getDepartments(), 'cartypes': Settings.getCarTypes()})
            return render_template('admin.cars_edit.html', **params)

        elif request.form.get('action') == 'updatecars':  # save car
            if request.form.get('car_id') != 'None':  # update car
                car = Car.getCars(id=request.form.get('car_id'))
                
            else:  # add car
                car = Car('', '', '', '', '', module[1])
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
            params.update({'car': Car.getCars(id=request.form.get('action').split('_')[-1]), 'departments': Department.getDepartments(), 'cartypes': Settings.getCarTypes()})
            return render_template('admin.cars_edit.html', **params)

        elif request.form.get('action').startswith('deletecars_'):  # delete car
            db.session.delete(Car.getCars(id=request.form.get('action').split('_')[-1]))
            db.session.commit()
    #try:
    #    params.update({'cars': classes.get('department').getDepartments(module[1]).getCars()})
    #except AttributeError:
    #    params.update({'cars': []})
    params.update({'cars': Department.getDepartments(module[1]).getCars()})
    return render_template('admin.cars.html', **params)
