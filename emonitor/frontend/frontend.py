from collections import OrderedDict
from flask import Blueprint, current_app, render_template, send_from_directory, request, jsonify
from flask.ext import login
from emonitor.user import User
from emonitor.extensions import classes, babel

frontend = Blueprint('frontend', __name__, template_folder="web/templates")
frontend.modules = OrderedDict()

babel.gettext(u'emonitor.monitorserver.MonitorServer')
babel.gettext(u'trigger.default')


def _addModule(module):
    if module.info['name'] not in frontend.modules.keys():
        frontend.modules[module.info['name']] = module

frontend.addModule = _addModule


@frontend.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_from_directory(frontend.root_path + '/web/img/', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@frontend.route('/', methods=['GET', 'POST'])
@frontend.route('/<module>', methods=['GET', 'POST'])
def frontendContent(module=u''):

    if module != "":
        if module == 'none':
            return render_template('frontend.area.html')
        try:
            current_mod = [frontend.modules[m] for m in frontend.modules if frontend.modules[m].info['path'] == module.split('/')[0]][0]
        except IndexError:
            current_mod = frontend.modules['startpages']
        return current_mod.getFrontendContent()
    current_mod = frontend.modules['startpages']
    return render_template('frontendframe.html', user=User.getUsers(login.current_user.get_id() or -1), current_mod=current_mod, modules=frontend.modules, app_name=current_app.config.get('PROJECT'), app_version=current_app.config.get('APP_VERSION'), areas=classes.get('settings').getFrontendSettings())


@frontend.route('/data/<path:module>', methods=['GET', 'POST'])
def getData(module=u''):
    current_mod = frontend.modules['startpages']

    try:
        current_mod = [frontend.modules[m] for m in frontend.modules if frontend.modules[m].info['path'] == module.split('/')[0]][0]
    except IndexError:
        current_app.logger.info("module '%s' not found" % module)

    result = current_mod.getFrontendData()
    if request.args.get('format') == 'json':
        result = jsonify(result)
    return result


# static folders
@frontend.route('/img/<path:filename>')
def imagebase_static(filename):
    return send_from_directory(frontend.root_path + '/web/img/', filename)


@frontend.route('/js/<path:filename>')
def jsbase_static(filename):
    return send_from_directory(frontend.root_path + '/web/js/', filename)


@frontend.route('/css/<path:filename>')
def cssbase_static(filename):
    return send_from_directory(frontend.root_path + '/web/css/', filename)


@frontend.route('/file/<path:filename>')
def filebase_static(filename):
    if filename.startswith('fax/'):
        filename = filename[4:]
        fpath = current_app.config.get('PATH_DONE')
    else:
        fpath = frontend.root_path + filename
    return send_from_directory(fpath, filename)
    #return send_from_directory(frontend.root_path + '/web/css/', filename)


@frontend.route('/fonts/<path:filename>')
def fontbase_static(filename):
    return send_from_directory(frontend.root_path + '/web/fonts/', filename)