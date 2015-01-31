
import os
import subprocess
from flask import render_template, request, current_app
from emonitor.extensions import classes, db
from emonitor.modules.printers.printerutils import PrintLayout


def getAdminContent(self, **params):
    """
    Deliver admin content of module printers

    :param params: use given parameters of request
    :return: rendered template as string
    """
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
            if len(callstring.split()) > 0:
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
                        templates[mod].append(PrintLayout('%s.%s' % (mod, f)))
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
                _s = [request.form.get('printersettings'), []]  # add settings from template
                for tparam in [_p for _p in request.form.get('templateparams').split(';') if _p != ""]:
                    _s[1].append('%s=%s' % (tparam[7:], request.form.get(tparam)))
                _s[1] = ';'.join(_s[1])
                p.settings = _s
                p.state = request.form.get('printerstate')
                db.session.commit()

            elif request.form.get('action').startswith('deleteprinters_'):  # delete printer definition
                db.session.delete(classes.get('printer').getPrinters(pid=request.form.get('action').split('_')[-1]))
                db.session.commit()

    params.update({'printers': classes.get('printer').getPrinters()})
    return render_template('admin.printers.html', **params)


def getAdminData(self):
    """
    Deliver admin content of module printers (ajax)

    :return: rendered template as string or json dict
    """

    if 'action' in request.args and request.args['action'] == 'loadtemplatepreview':  # load template parameters
        pl = PrintLayout(request.args.get('template'))
        module = request.args.get('template').split('.')[0]
        t = request.args.get('template').split('.')[2]
        values = {}
        for v in request.args.get('values').split(';'):
            if '=' in v and len(v.split('=')) == 2:
                _v = v.split('=')
                values[_v[0]] = _v[1]
        return {'parameters': render_template('admin.printers_parameters.html', parameters=pl.getParameters(), values=values), 'url': '/%s/export/999999-%s.html' % (module, t)}

    return ""
