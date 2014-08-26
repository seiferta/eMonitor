import os
import re
from flask import current_app, render_template, request, send_from_directory
import werkzeug

from emonitor.extensions import classes, db
from alarmkeysupload import XLSFile, buildDownloadFile

uploadfiles = {}


def getAdminContent(self, **params):
    module = request.view_args['module'].split('/')

    if len(module) < 2:
        module.append(u'1')
    
    if len(module) > 2 and module[2] == 'upload':  # upload alarmkeys
        params.update({'': int(module[1]), 'department': module[1]})
        return render_template('admin.alarmkeys.upload.html', **params)
    
    else:
        depid = 1
        try:
            if int(module[1]):
                depid = int(module[1])
        except:
            pass
            
        if request.method == 'POST':
            if request.form.get('action') == 'adddefault':  # add default aao
                params.update({'alarmkey': classes.get('alarmkey')('', '', '', ''), 'depid': depid, 'departments': classes.get('department').getDepartments(), 'cars': classes.get('car').getCars(), 'type': 0})
                return render_template('admin.alarmkeys_actions.html', **params)

            elif request.form.get('action') == 'savedefault':  # save default aao
                alarmkeycar = classes.get('alarmkeycar').getAlarmkeyCars(kid=0, dept=request.form.get('deptid'))
                if not alarmkeycar or len(alarmkeycar) == 0:  # add
                    alarmkeycar = classes.get('alarmkeycar')(0, request.form.get('deptid'), '', '', '')
                    db.session.add(alarmkeycar)

                alarmkeycar.cars1(request.form.get('cars1'))
                alarmkeycar.cars2(request.form.get('cars2'))
                alarmkeycar.material(request.form.get('material'))
                
                if request.form.get('cars1') == request.form.get('cars2') == request.form.get('material') == '':  # remove
                    db.session.delete(alarmkeycar)
                db.session.commit()
                
            elif request.form.get('action') == 'editdefault':  # edit default aao
                params.update({'alarmkey': classes.get('alarmkey')('', '', '', ''), 'depid': depid, 'departments': classes.get('department').getDepartments(), 'cars': classes.get('car').getCars(), 'type': -1})
                return render_template('admin.alarmkeys_actions.html', **params)

            elif request.form.get('action') == 'addkey':  # add key
                params.update({'alarmkey': classes.get('alarmkey')('', '', '', ''), 'depid': depid, 'departments': classes.get('department').getDepartments(), 'cars': classes.get('car').getCars(), 'type': -2})
                return render_template('admin.alarmkeys_actions.html', **params)

            elif request.form.get('action') == 'savekey':  # save key
                if request.form.get('keyid') == 'None':  # add new
                    alarmkey = classes.get('alarmkey')('', '', '', '')
                    db.session.add(alarmkey)
                    db.session.commit()

                else:  # update existing
                    alarmkey = classes.get('alarmkey').getAlarmkeys(request.form.get('keyid'))

                alarmkey.category = request.form.get('category')
                alarmkey.key = request.form.get('key')
                alarmkey.key_internal = request.form.get('keyinternal')
                alarmkey.remark = request.form.get('remark')
                alarmkey.setCars(int(request.form.get('deptid')), cars1=request.form.get('cars1'), cars2=request.form.get('cars2'), materials=request.form.get('material'))
                db.session.commit()
                
            elif request.form.get('action').startswith('deletecars_'):  # delete car definition
                _op, _kid, _dept = request.form.get('action').split('_')
                keycar = classes.get('alarmkeycar').getAlarmkeyCars(kid=_kid, dept=_dept)
                if keycar:
                    db.session.delete(keycar)
                
                # delete key if no definied cars
                if len(classes.get('alarmkeycar').getAlarmkeyCars(kid=_kid)) == 0:
                    key = classes.get('alarmkey').getAlarmkeys(id=_kid)
                    db.session.delete(key)

                db.session.commit()
                
            elif request.form.get('action').startswith('editcars_'):  # edit key with cars
                _op, _kid, _dept = request.form.get('action').split('_')
                params.update({'alarmkey': classes.get('alarmkey').getAlarmkeys(id=_kid), 'depid': _dept, 'departments': classes.get('department').getDepartments(), 'cars': classes.get('car').getCars(), 'type': 1})
                return render_template('admin.alarmkeys_actions.html', **params)

        alarmkeys_count = []
        counted_keys = classes.get('alarmkey').query.from_statement('select category, count(key) as key, id from alarmkeys group by category order by id;')
        _sum = 0
        for r in counted_keys.all():
            alarmkeys_count.append((r.category, r.key))
            _sum += int(r.key)

        params.update({'alarmkeys_count': alarmkeys_count, 'depid': depid, 'defaultcars': classes.get('alarmkey').getDefault(depid), 'sum': _sum})
        return render_template('admin.alarmkeys.html', **params)


def getAdminData(self):
    if request.args.get('action') == 'loaddetails':  # details for given key
        return render_template('admin.alarmkeys.detail.html', keys=classes.get('alarmkey').getAlarmkeysByCategory(request.args.get('category').replace('__', ' ')), department=request.args.get('department'))  # macro='detail_row' TODO

    elif request.args.get('action') == 'upload':
        if request.files:
            uploadfile = request.files['uploadfile']
            filename = werkzeug.secure_filename(uploadfile.filename)
            fname = os.path.join(current_app.config.get('PATH_TMP'), filename)
            uploadfile.save(fname)
            xlsfile = XLSFile(fname)
            uploadfiles[uploadfile.filename] = xlsfile

            return render_template('admin.alarmkeys.upload2.html', sheets=uploadfiles[uploadfile.filename].getSheets())
            
    elif request.args.get('action') == 'upload_sheet':  # sheet selector
        definitionfile = uploadfiles[request.args.get('filename')]
        return render_template('admin.alarmkeys.upload3.html', cols=definitionfile.getCols(request.args.get('sheetname')))

    elif request.args.get('action') == 'testimport':  # build data for preview
        col_definition = {'dept': request.args.get('department'), 'sheet': request.args.get('sheetname'),
                          'category': request.form.get('category'), 'key': request.form.get('key'),
                          'keyinternal': request.form.get('keyinternal'), 'remark': request.form.get('remark'),
                          'cars1': request.form.getlist('cars1'), 'cars2': request.form.getlist('cars2'),
                          'material': request.form.getlist('material')}

        deffile = uploadfiles[request.args.get('filename')]
        vals = deffile.getValues(col_definition)
        return render_template('admin.alarmkeys.uploadpreview.html', vals=vals)

    elif request.args.get('action') == 'doimport':  # do import and store values
        coldefinition = {'dept': request.args.get('department'), 'sheet': request.args.get('sheetname'),
                         'category': request.form.get('category'), 'key': request.form.get('key'),
                         'keyinternal': request.form.get('keyinternal'), 'remark': request.form.get('remark'),
                         'cars1': request.form.getlist('cars1'), 'cars2': request.form.getlist('cars2'),
                         'material': request.form.getlist('material')}
        deffile = uploadfiles[request.args.get('filename')]

        vals = deffile.getValues(coldefinition)
        states = []

        if request.form.get('add_material'):  # add new material
            p = re.compile(r'<.*?>')
            for k in vals['carsnotfound']:
                n_car = vals['carsnotfound'][k]
                n_car.name = p.sub('', n_car.name)
                if n_car.name == '':
                    continue
                db.session.add(n_car)
            db.session.commit()
            
        if request.form.get('add_new'):  # add new keys ( item state=-1)
            states.append('-1')
            
        if request.form.get('add_update'):  # update existing keys (item state=1)
            states.append('1')
        
        for key in vals['keys']:  # item list
            if key['state'] in states:  # import only with correct state
                
                if key['state'] == '-1':  # add key
                    k = classes.get('alarmkey')(key['category'], key['key'], key['keyinternal'], key['remark'])
                    db.session.add(k)
                    db.session.commit()
                    k.setCars(coldefinition['dept'],
                              cars1=";".join([str(c.id) for c in key['cars1']]),
                              cars2=";".join([str(c.id) for c in key['cars2']]),
                              materials=";".join([str(c.id) for c in key['material']]))
                    db.session.commit()
                    key['state'] = '0'

                elif key['state'] == '1':  # update key
                    k = classes.get('alarmkey').getAlarmkeys(id=int(key['dbid']))
                    k.category = key['category']
                    k.key = key['key']
                    k.key_internal = key['keyinternal']
                    k.remark = key['remark']
                    k.setCars(coldefinition['dept'],
                              cars1=';'.join(filter(None, key['cars1_ids'])),
                              cars2=';'.join(filter(None, key['cars2_ids'])),
                              materials=';'.join(filter(None, key['material_ids'])))
                    db.session.commit()
        return ""
        
    elif request.args.get('action') == 'download':
        # build exportfile
        filename = buildDownloadFile(request.args.get('department'), request.args.get('options'))
        if filename != "":
            return filename
            
    elif request.args.get('action') == 'keyslookup':
        keys = {}
        
        for k in classes.get('alarmkey').getAlarmkeys():
            keys[str(k.id)] = '%s: %s' % (k.category, k.key)
        return keys
        
    elif request.args.get('action') == 'categorylookup':
        key = classes.get('alarmkey').getAlarmkeys(id=int(request.args.get('keyid')))
        return {'id': key.id, 'category': key.category}

    if "/download/" in request.url:  # deliver file
        filename = os.path.basename(request.url)
        mime = "application/x.download"
        if filename.endswith('.xlsx'):
            mime = "application/vnd.ms-excel"
        return send_from_directory("%s/" % current_app.config.get('PATH_TMP'), filename, as_attachment=True, mimetype=mime)
    return ""
