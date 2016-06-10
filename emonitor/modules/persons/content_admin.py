import os
import werkzeug
import yaml
from datetime import datetime
from flask import render_template, request, current_app
from emonitor.extensions import db
from emonitor.modules.persons.persons import Person
from emonitor.modules.settings.settings import Settings
from personsupload import XLSFile

uploadfiles = {}


def getAdminContent(self, **params):
    module = request.view_args['module'].split('/')

    if len(module) < 2:
        module.append(u'1')

    if len(module) > 2 and module[2] == 'upload':  # upload persons
        params.update({'': int(module[1]), 'depid': module[1]})
        return render_template('admin.persons.upload.html', **params)

    if request.method == 'POST':
        if request.form.get('action') == 'createperson':  # add person
            params.update({'person': Person('', '', '', '', '', '', False, datetime.now(), '', int(module[1])), 'settings': Settings.get('persons.settings')})
            return render_template('admin.persons_edit.html', **params)

        elif request.form.get('action').startswith('editperson_'):  # edit person
            params.update({'person': Person.getPersons(id=request.form.get('action').split('_')[-1]), 'settings': Settings.get('persons.settings')})
            return render_template('admin.persons_edit.html', **params)

        elif request.form.get('action') == 'updateperson':  # save person
            if request.form.get('person_id') != 'None':
                person = Person.getPersons(id=request.form.get('person_id'))
            else:
                person = Person('', '', '', '', '', '', False, datetime.now(), '', int(module[1]))
                db.session.add(person)

            person.firstname = request.form.get('firstname')
            person.lastname = request.form.get('lastname')
            person.salutation = request.form.get('salutation')
            person.grade = request.form.get('grade')
            person._dept = int(request.form.get('dept'))
            person.position = request.form.get('position')
            person.active = 'active' in request.form.keys()
            try:
                person.birthdate = datetime.strptime('{} 00:00:00'.format(request.form.get('birthdate')), "%d.%m.%Y %H:%M:%S")
            except ValueError:
                pass
            person.identifier = request.form.get('identifier')
            person.remark = request.form.get('remark')
            _additional = {}
            for field in Settings.get('persons.settings').get('additional'):
                if field.split('=')[0] in request.form.keys() and request.form.get(field.split('=')[0]).strip() != '':
                    _additional[field.split('=')[0]] = request.form.get(field.split('=')[0])
            person._options = yaml.safe_dump(_additional, encoding='utf-8')
            db.session.commit()

        elif request.form.get('action').startswith('deleteperson_'):
            db.session.delete(Person.getPersons(id=request.form.get('action').split('_')[-1]))
            db.session.commit()

        elif request.form.get('action') == 'updategrades':
            grades = request.form.getlist('grade')
            while grades[-1] == grades[-2] == u"":  # remove last empty entries
                grades = grades[:-2]
            _settings = Settings.get('persons.settings')
            if 'positions' not in _settings.keys():
                _settings['positions'] = []
            _settings['grades'] = zip(*[grades[i::2] for i in range(2)])
            Settings.set('persons.settings', _settings)
            db.session.commit()

        elif request.form.get('action') == 'updatepositions':
            _settings = Settings.get('persons.settings')
            if 'grades' not in _settings.keys():
                _settings['grades'] = []
            _settings['positions'] = request.form.get('positions').replace('\r', '').split('\n')
            Settings.set('persons.settings', _settings)
            db.session.commit()

        elif request.form.get('action') == 'updateadditional':
            _settings = Settings.get('persons.settings')
            if 'additional' not in _settings.keys():
                _settings['additional'] = []
            _settings['additional'] = request.form.get('additional').replace('\r', '').split('\n')
            Settings.set('persons.settings', _settings)
            db.session.commit()

    if int(module[1]) == 0:
        params.update({'settings': Settings.get('persons.settings')})
        return render_template("admin.persons.settings.html", **params)
    persons = Person.getPersons(dept=int(module[1]))
    chars = {}
    for p in persons:
        chars[p.fullname[0].upper()] = 0
    params.update({'persons': persons, 'chars': sorted(chars), 'depid': module[1]})
    return render_template("admin.persons.html", **params)


def getAdminData(self):
    if request.args.get('action') == '':
        pass

    elif request.args.get('action') == 'upload':
        if request.files:
            uploadfile = request.files['uploadfile']
            filename = werkzeug.secure_filename(uploadfile.filename)
            fname = os.path.join(current_app.config.get('PATH_TMP'), filename)
            uploadfile.save(fname)
            xlsfile = XLSFile(fname)
            uploadfiles[uploadfile.filename] = xlsfile
            return render_template('admin.persons.upload2.html', sheets=uploadfiles[uploadfile.filename].getSheets())

    elif request.args.get('action') == 'upload_sheet':  # sheet selector
        definitionfile = uploadfiles[request.args.get('filename')]
        return render_template('admin.persons.upload3.html', cols=definitionfile.getCols(request.args.get('sheetname')))

    elif request.args.get('action') == 'testimport':  # build data for preview
        col_definition = dict(zip(request.form.keys(), request.form.values()))
        col_definition.update({'sheet': request.args.get('sheetname'), 'department': request.args.get('department')})

        deffile = uploadfiles[request.args.get('filename')]
        vals = deffile.getValues(col_definition)
        return render_template('admin.persons.uploadpreview.html', vals=vals)

    elif request.args.get('action') == 'doimport':  # do import and store values
        col_definition = dict(zip(request.form.keys(), request.form.values()))
        col_definition.update({'sheet': request.args.get('sheetname'), 'department': request.args.get('department')})

        deffile = uploadfiles[request.args.get('filename')]

        vals = deffile.getValues(col_definition)
        states = []

        if request.form.get('add_new'):  # add new keys ( item state=-1)
            states.append('-1')

        if request.form.get('add_update'):  # update existing keys (item state=1)
            states.append('1')

        for key in vals['persons']:  # item list
            if key['state'] in states:  # import only with correct state
                if key['state'] == '-1':  # add key
                    try:
                        key['birthdate'] = datetime.strptime(key['birthdate'], '%d.%m.%Y')
                    except:
                        pass
                    key['active'] = key['active'] == 'Aktiv'
                    p = Person(key['firstname'], key['lastname'], key['salutation'], key['grade'], key['position'], key['identifier'], key['active'], key['birthdate'], key['remark'], int(request.args.get('department')))
                    db.session.add(p)
                    db.session.commit()
                    key['state'] = '0'

                elif key['state'] == '1':  # update key
                    p = Person.getPersons(id=key['dbid'])
                    if p:
                        p.firstname = key['firstname']
                        p.lastname = key['lastname']
                        p.grade = key['grade']
                        p.position = key['position']
                        db.session.commit()
        return ""
