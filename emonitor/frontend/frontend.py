"""
Basic framework for frontend area (blueprint).
Modules can register a frontend area that will be loaded automaticaly into the area with an own menu entry.

Use the info parameter of the module implementation:
::

    info = dict(area=['frontend'], name='modulename', path='modulepath', ...)

This example will add the module 'modulename' in frontend area with url `server/modulepath`
"""
from collections import OrderedDict
from flask import Blueprint, current_app, render_template, send_from_directory, request, jsonify
import flask_login as login
from emonitor.user import User
from emonitor.extensions import babel, signal
from emonitor.utils import restartService
from emonitor.socketserver import SocketHandler

frontend = Blueprint('frontend', __name__, template_folder="web/templates")
frontend.modules = OrderedDict()

babel.gettext(u'emonitor.monitorserver.MonitorServer')
babel.gettext(u'trigger.default')

from emonitor.modules.settings.settings import Settings


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
    """
    Frontend area is reachable under *http://[servername]:[port]/[module]*

    :param module: module name as string
    :return: renderd HTML-outpu of module or startpage
    """
    if module != "":
        if module == 'none':
            return render_template('frontend.area.html')
        try:
            current_mod = [frontend.modules[m] for m in frontend.modules if frontend.modules[m].info['path'] == module.split('/')[0]][0]
        except IndexError:
            current_mod = frontend.modules['startpages']
        return current_mod.getFrontendContent()
    current_mod = frontend.modules['startpages']
    return render_template('frontendframe.html', user=User.getUsers(login.current_user.get_id() or -1), current_mod=current_mod, modules=frontend.modules, app_name=current_app.config.get('PROJECT'), app_version=current_app.config.get('APP_VERSION'), areas=Settings.getFrontendSettings())


@frontend.route('/data/<path:module>', methods=['GET', 'POST'])
def getData(module=u''):
    """
    Frontend area is reachable unter `http://[servername]:[port]/data/[module]`

    This path is used to run background operations (e.g. ajax calls) and delivers the result of the `getFrontendData`
    method of the module. If **format=json** in the url the result will be formated as json

    :param module: module name as string
    :return: return value of `getFrontendData` method of `module`
    """
    current_mod = frontend.modules['startpages']

    if module == u"frontpage" and 'action' in request.args:
        if request.args.get('action') == 'info':
            return render_template('frontend.emonitorinfo.html', app_name=current_app.config.get('PROJECT'), app_version=current_app.config.get('APP_VERSION'))
        elif request.args.get('action') == 'systeminfo':
            return render_template('frontend.systeminfo.html')
        elif request.args.get('action') == 'restart':
            from emonitor.extensions import scheduler
            scheduler.add_job(restartService)
            return ""
        elif request.args.get('action') == 'translatebaseinfo':
            return jsonify({'connection_info': babel.gettext(u'frontend.connection_info')})

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
    """
    Register url path *http://[servername]:[port]/img/[filename]* for static files

    :param filename: filename as string
    """
    return send_from_directory(frontend.root_path + '/web/img/', filename)


@frontend.route('/js/<path:filename>')
def jsbase_static(filename):
    """
    Register url path *http://[servername]:[port]/js/[filename]* for static files

    :param filename: filename as string
    """
    return send_from_directory(frontend.root_path + '/web/js/', filename)


@frontend.route('/css/<path:filename>')
def cssbase_static(filename):
    """
    Register url path *http://[servername]:[port]/css/[filename]* for static files

    :param filename: filename as string
    """
    return send_from_directory(frontend.root_path + '/web/css/', filename)


@frontend.route('/file/<path:filename>')
def filebase_static(filename):
    """
    Register url path *http://[servername]:[port]/file/[filename]* for static files

    :param filename: filename as string
    """
    if filename.startswith('fax/'):
        filename = filename[4:]
        fpath = current_app.config.get('PATH_DONE')
    else:
        fpath = frontend.root_path + filename
    return send_from_directory(fpath, filename)


@frontend.route('/fonts/<path:filename>')
def fontbase_static(filename):
    """
    Register url path *http://[servername]:[port]/fonts/[filename]* for static files

    :param filename: filename as string
    """
    return send_from_directory(frontend.root_path + '/web/fonts/', filename)
