
import os
import subprocess
from flask import render_template, request, current_app
from emonitor.extensions import classes, db


def getAdminContent(self, **params):

    module = request.view_args['module'].split('/')

    if len(module) == 2:
        if module[1] == 'settings':  # printer settings
            if request.method == 'POST':
                if request.form.get('action') == 'savereprintersparams':
                    classes.get('settings').set('printer.callstring', request.form.get('printers_callstring'))

            _p = dict()
            _p['callstring'] = classes.get('settings').get('printer.callstring')
            params.update({'params': _p})
            return render_template('admin.printers.settings.html', **params)
    else:

        def _printernames(callstring):
            printernames = ['<default>']
            callstring = '%s -printer "xxx"' % callstring.split()[0]
            try:
                subprocess.check_output(callstring, stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                for l in e.output.split('\r\n'):
                    if l.startswith('  "'):
                        printernames.append(l[3:-1].strip())
            return printernames

        #def _callstring():  # get callstring and replace variables
        #    callstring = classes.get('settings').get('printer.callstring')
        #    callstring = callstring.replace('[basepath]', current_app.config.get('PROJECT_ROOT'))
        #    return callstring

        def _templates():  # get all printer templates
            templates = {}
            for root, dirs, files in os.walk("%s/emonitor/modules/" % current_app.config.get('PROJECT_ROOT')):
                mod = root.replace("%s/emonitor/modules/" % current_app.config.get('PROJECT_ROOT'), '').replace('\\templates', '')
                for f in files:
                    if f.endswith('.html') and f.startswith('print.'):
                        if mod not in templates:
                            templates[mod] = []
                        templates[mod].append(f)
            return templates

        if request.method == 'POST':
            if request.form.get('action') == 'createprinter':  # add printer definition
                printer = classes.get('printer')('', '', '', '', "['1']")
                params.update({'printer': printer, 'templates': _templates(), 'printernames': sorted(_printernames(printer.getCallString()))})
                return render_template('admin.printers_actions.html', **params)

            elif request.form.get('action').startswith('editprinters_'):
                printer = classes.get('printer').getPrinters(int(request.form.get('action').split('_')[-1]))
                params.update({'printer': printer, 'templates': _templates(), 'printernames': sorted(_printernames(printer.getCallString()))})
                return render_template('admin.printers_actions.html', **params)

            elif request.form.get('action') == 'updateprinter':
                if request.form.get('printer_id') == 'None':  # add new printerdefintion
                    p = classes.get('printer')('', '', '', '', settings="", state=0)
                    db.session.add(p)
                else:
                    p = classes.get('printer').getPrinters(int(request.form.get('printer_id')))
                p.name = request.form.get('printername')
                p.printer = request.form.get('printerprinter')
                p.module = request.form.get('template').split('.')[0]
                p.layout = '.'.join(request.form.get('template').split('.')[1:])
                p.settings = request.form.getlist('printersettings')
                p.state = request.form.get('printerstate')
                db.session.commit()

            elif request.form.get('action').startswith('deleteprinters_'):  # delete printer definition
                db.session.delete(classes.get('printer').getPrinters(pid=request.form.get('action').split('_')[-1]))
                db.session.commit()

    params.update({'printers': classes.get('printer').getPrinters()})
    return render_template('admin.printers.html', **params)


def getAdminData(self, params={}):
    return ""