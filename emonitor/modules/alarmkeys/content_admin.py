import os
import re
from sqlalchemy import func
from flask import current_app, json, render_template, request, send_from_directory, jsonify
import werkzeug
import datetime
import codecs

from emonitor.extensions import db, babel
from emonitor.modules.alarmkeys.alarmkey import Alarmkey
from emonitor.modules.alarmkeys.alarmkeyset import AlarmkeySet, AlarmkeySetBase
from emonitor.modules.alarmkeys.alarmkeycar import AlarmkeyCars
from emonitor.modules.settings.department import Department
from emonitor.modules.cars.car import Car
from alarmkeysupload import XLSFile, buildDownloadFile

uploadfiles = {}


def getAdminContent(self, **params):
    """
    Deliver admin content of module alarmkeys

    :param params: use given parameters of request
    :return: rendered template as string
    """
    module = request.view_args['module'].split('/')

    if len(module) < 2:
        module.append(u'1')
    
    if len(module) > 2 and module[2] == 'upload':  # upload alarmkeys
        params.update({'': int(module[1]), 'department': module[1]})
        return render_template('admin.alarmkeys.upload.html', **params)
    
    else:
        depid = 1
        try:
            if module[1].isnumeric():
                depid = int(module[1])
        except:
            pass

        if request.method == 'POST':
            if depid == 0:
                if request.form.get('action', '') == 'createset':  # add alarmkeyset
                    params.update({'alarmkeyset': AlarmkeySet('', '', datetime.date.today(), datetime.date.today(), ''), 'setbases': AlarmkeySet.getBases(), 'orphankeys': Alarmkey.getOrphanKeys()})
                    return render_template('admin.alarmkeys.set_actions.html', **params)

                elif request.form.get('action', '').startswith('deleteset_'):
                    db.session.delete(AlarmkeySet.getAlarmkeySets(request.form.get('action', '').split('_')[-1]))
                    db.session.commit()

                elif request.form.get('action', '').startswith('detailset_'):  # edit alarmkeyset
                    params.update({'alarmkeyset': AlarmkeySet.getAlarmkeySets(request.form.get('action').split('_')[-1]), 'setbases': AlarmkeySet.getBases(), 'orphankeys': Alarmkey.getOrphanKeys()})
                    return render_template('admin.alarmkeys.set_actions.html', **params)

                elif request.form.get('action', '') == 'savealarmkeyset':  # save alarmkeyset
                    if request.form.get('set_id', '') == 'None':  # add
                        akset = AlarmkeySet('', '', datetime.date.today(), datetime.date.today(), '')
                        db.session.add(akset)
                    else:
                        akset = AlarmkeySet.getAlarmkeySets(request.form.get('set_id'))
                    akset.name = request.form.get('set_name')
                    if request.form.get('set_startdate', '') != "":
                        akset.startdate = datetime.datetime.strptime(request.form.get('set_startdate'), '%d.%m.%Y')
                    else:
                        akset.startdate = None
                    if request.form.get('set_enddate', '') != "":
                        akset.enddate = datetime.datetime.strptime(request.form.get('set_enddate'), '%d.%m.%Y')
                    else:
                        akset.enddate = None
                    akset.remark = request.form.get('set_remark')
                    akset.base = request.form.get('set_base')
                    db.session.commit()
                    if 'set_assignorphan' in request.form.keys():  # add all orphan keys to current set
                        for key in Alarmkey.getOrphanKeys():
                            key._keyset = int(akset.id)
                        db.session.commit()

                elif request.form.get('action', '').startswith('deletebase_'):
                    if os.path.exists("{}alarmkeysetbase/{}".format(current_app.config.get('PATH_DATA'), "_".join(request.form.get('action', '').split('_')[1:]))):
                        os.remove("{}alarmkeysetbase/{}".format(current_app.config.get('PATH_DATA'), "_".join(request.form.get('action', '').split('_')[1:])))

                params.update({'aksets': AlarmkeySet.getAlarmkeySets(), 'akbases': AlarmkeySet.getBases()})
                return render_template('admin.alarmkeys.set_list.html', **params)

            if request.form.get('action') == 'adddefault':  # add default aao
                params.update({'alarmkey': Alarmkey('', '', '', ''), 'depid': depid, 'departments': Department.getDepartments(), 'cars': Car.getCars(), 'type': 0})
                return render_template('admin.alarmkeys_actions.html', **params)

            elif request.form.get('action') == 'savedefault':  # save default aao
                alarmkeycar = AlarmkeyCars.getAlarmkeyCars(kid=9999, dept=request.form.get('deptid'))  # 9999 = default department
                if not alarmkeycar:  # add
                    alarmkeycar = AlarmkeyCars(9999, request.form.get('deptid'), '', '', '')
                    db.session.add(alarmkeycar)

                alarmkeycar.cars1 = request.form.get('cars1')
                alarmkeycar.cars2 = request.form.get('cars2')
                alarmkeycar.materials = request.form.get('material')
                if alarmkeycar.kid != 9999 and request.form.get('cars1') == request.form.get('cars2') == request.form.get('material') == '':  # remove
                    db.session.delete(alarmkeycar)
                db.session.commit()
                
            elif request.form.get('action') == 'editdefault':  # edit default aao
                params.update({'alarmkey': Alarmkey('', '', '', ''), 'depid': depid, 'departments': Department.getDepartments(), 'aksets': AlarmkeySet.getAlarmkeySets(), 'cars': Car.getCars(), 'type': -1})
                return render_template('admin.alarmkeys_actions.html', **params)

            elif request.form.get('action') == 'addkey':  # add key
                params.update({'alarmkey': Alarmkey('', '', '', ''), 'depid': depid, 'departments': Department.getDepartments(), 'aksets': AlarmkeySet.getAlarmkeySets(), 'cars': Car.getCars(), 'type': -2})
                return render_template('admin.alarmkeys_actions.html', **params)

            elif request.form.get('action') == 'savekey':  # save key
                if request.form.get('keyid') == 'None':  # add new
                    alarmkey = Alarmkey('', '', '', '')
                    db.session.add(alarmkey)
                    db.session.commit()

                else:  # update existing
                    alarmkey = Alarmkey.getAlarmkeys(request.form.get('keyid'))

                alarmkey.category = request.form.get('category')
                alarmkey.key = request.form.get('key')
                alarmkey.key_internal = request.form.get('keyinternal')
                alarmkey.remark = request.form.get('remark')
                if request.form.get('keyset', '') == '':
                    alarmkey._keyset = None
                else:
                    alarmkey._keyset = request.form.get('keyset')
                alarmkey.setCars(int(request.form.get('deptid')), cars1=request.form.get('cars1'), cars2=request.form.get('cars2'), material=request.form.get('material'))

                alarmkey.keysetitem = None
                if request.form.get('keyset', '') != "":
                    keyset = AlarmkeySet.getAlarmkeySets(request.form.get('keyset'))
                    if keyset:
                        item = filter(lambda x: x.get('stichwort') == alarmkey.category and x.get('schlagwort') == alarmkey.key, keyset.alarmkeys)
                        if len(item) > 0:
                            alarmkey.keysetitem = item[0].get('nr')
                db.session.commit()  # readd

            elif request.form.get('action').startswith('deletecars_'):  # delete car definition
                _op, _kid, _dept = request.form.get('action').split('_')
                keycar = AlarmkeyCars.getAlarmkeyCars(kid=_kid, dept=_dept)
                if keycar:
                    db.session.delete(keycar)
                    db.session.commit()

                # delete key if no definied cars
                if len(AlarmkeyCars.getAlarmkeyCars(kid=_kid)) == 0:
                    key = Alarmkey.getAlarmkeys(id=_kid)
                    db.session.delete(key)
                db.session.commit()
                
            elif request.form.get('action').startswith('editcars_'):  # edit key with cars
                _op, _kid, _dept = request.form.get('action').split('_')
                params.update({'alarmkey': Alarmkey.getAlarmkeys(id=_kid), 'depid': _dept, 'departments': Department.getDepartments(), 'aksets': AlarmkeySet.getAlarmkeySets(), 'cars': Car.getCars(), 'type': 1})
                return render_template('admin.alarmkeys_actions.html', **params)

        if depid == 0:  # edit options
            params.update({'aksets': AlarmkeySet.getAlarmkeySets(), 'departments': Department.getDepartments(), 'akbases': AlarmkeySet.getBases()})
            return render_template('admin.alarmkeys.set_list.html', **params)

        params.update({'depid': depid, 'defaultcars': Alarmkey.getDefault(depid), 'aksets': AlarmkeySet.getAlarmkeySets()})
        return render_template('admin.alarmkeys.html', **params)


def getAdminData(self):
    """
    Deliver admin content of module alarmkeys (ajax)

    :return: rendered template as string or json dict
    """
    if request.args.get('action') == 'loaddetails':  # details for given key
        return render_template('admin.alarmkeys.detail.html', keys=Alarmkey.getAlarmkeysByCategoryId(request.args.get('category'), keysetid=int(request.args.get('keysetid', 0))), department=request.args.get('department'))

    elif request.args.get('action', '') == "changekeyset":  # deliver alarmkeys for given set
        ak = Alarmkey
        if request.args.get('keysetid', '0') == '0':
            counted_keys = db.get(ak.category.label('category'), func.count(ak.key).label('key'), ak.id.label('id'), func.count(ak.id).label('keysetcount')).group_by(ak.category).filter_by(_keyset=None)
        else:
            counted_keys = db.get(ak.category.label('category'), func.count(ak.key).label('key'), ak.id.label('id'), func.count(ak.id).label('keysetcount')).group_by(ak.category).filter_by(_keyset=request.args.get('keysetid'))
        _sum = 0
        alarmkeys_count = []
        for r in counted_keys.all():
            alarmkeys_count.append([r.category, r.key, r.id])
            _sum += int(r.key)
        return render_template('admin.alarmkeys.macro.html', alarmkeys_count=alarmkeys_count, depid=request.args.get('department'), sum=_sum)

    elif request.args.get('action') == 'upload':
        if request.files:
            uploadfile = request.files['uploadfile']
            fname = os.path.join(current_app.config.get('PATH_TMP'), werkzeug.secure_filename(uploadfile.filename))
            uploadfile.save(fname)
            uploadfiles[uploadfile.filename] = XLSFile(fname)

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
        return render_template('admin.alarmkeys.uploadpreview.html', vals=deffile.getValues(col_definition), keysets=AlarmkeySet.getAlarmkeySets())

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
            db.session.flush()
            
        if request.form.get('add_new'):  # add new keys ( item state=-1)
            states.append('-1')

        if request.form.get('add_update'):  # update existing keys (item state=1)
            states.append('1')

        if request.form.get('add_assign') and request.form.get('keyset', '') != '':  # assign keys to keyset (item state=2)
            keyset = AlarmkeySet.getAlarmkeySets(request.form.get('keyset'))
            states.append('2')

        for key in vals['keys']:  # item list
            if key['state'] in states:  # import only with correct state
                
                if key['state'] == '-1':  # add key
                    k = Alarmkey(key['category'], key['key'], key['keyinternal'], key['remark'])
                    db.session.add(k)
                    db.session.flush()
                    k.setCars(coldefinition['dept'],
                              cars1=";".join([str(c.id) for c in key['cars1']]),
                              cars2=";".join([str(c.id) for c in key['cars2']]),
                              materials=";".join([str(c.id) for c in key['material']]))
                    db.session.commit()
                    key['state'] = '0'

                elif key['state'] == '1':  # update key
                    k = Alarmkey.getAlarmkeys(id=int(key['dbid']))
                    k.category = key['category']
                    k.key = key['key']
                    k.key_internal = key['keyinternal']
                    k.remark = key['remark']
                    k.setCars(coldefinition['dept'],
                              cars1=';'.join(filter(None, key['cars1_ids'])),
                              cars2=';'.join(filter(None, key['cars2_ids'])),
                              materials=';'.join(filter(None, key['material_ids'])))
                    db.session.commit()

                if '2' in states:  # assign keys to keyset
                    item = filter(lambda x: x.get('stichwort') == k.category and x.get('schlagwort') == k.key, keyset.alarmkeys)
                    k._keyset = keyset.id
                    if len(item) > 0:
                        k.keysetitem = item[0].get('nr')

        db.session.commit()
        return ""
        
    elif request.args.get('action') == 'download':
        # build exportfile
        filename = buildDownloadFile(request.args.get('department'), request.args.get('options'))
        if filename != "":
            return filename
            
    elif request.args.get('action') == 'keyslookup':
        keys = {}
        
        for k in Alarmkey.getAlarmkeys(keysetid=request.args.get('keysetid')):
            keys[str(k.id)] = '%s: %s' % (k.category, k.key)
        return keys

    elif request.args.get('action') == 'categorylookup':
        key = Alarmkey.getAlarmkeys(id=int(request.args.get('keyid')))
        return {'id': key.id, 'category': key.category}

    elif request.args.get('action', '') == 'keysetlookup':
        try:
            return AlarmkeySet.getAlarmkeySets(request.args.get('setid')).alarmkeys
        except ValueError:  # no base given
            return []

    elif request.args.get('action', '') == 'uploaddefinition':
        if request.files:
            ufile = request.files['uploadfile']
            if not os.path.exists("{}alarmkeysetbase/".format(current_app.config.get('PATH_DATA'))):
                os.makedirs("{}alarmkeysetbase/".format(current_app.config.get('PATH_DATA')))
            fname = os.path.join("{}alarmkeysetbase/".format(current_app.config.get('PATH_DATA')), ufile.filename)
            ufile.save(fname)
            with codecs.open(fname, 'r', encoding='utf-8') as fin:
                aksetbase = AlarmkeySetBase(ufile.filename, json.load(fin), 'external')
                return jsonify(state="ok", name=aksetbase.name, startdate=datetime.datetime.strftime(aksetbase.start, "%d.%m.%Y"), items=len(aksetbase.items), filename=aksetbase.id, type=aksetbase.settype)

        return jsonify(state="error")

    elif request.args.get('action', '') == 'createbaseset':
        """
        create base keys for given set and return number of updated
        """
        stats = AlarmkeySet.getAlarmkeySets(id=request.args.get('setid')).createBaseKeys()
        return babel.gettext('alarmkeys.createbaseset.result', num_success=stats[0], num_error=stats[1])

    if "/download/" in request.url:  # deliver file
        filename = os.path.basename(request.url)
        mime = "application/x.download"
        if filename.endswith('.xlsx'):
            mime = "application/vnd.ms-excel"
        return send_from_directory("%s/" % current_app.config.get('PATH_TMP'), filename, as_attachment=True, mimetype=mime)
    return ""
