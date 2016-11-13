"""
Basic framework for admin area (blueprint).
Modules can register an admin area that will be loaded automaticaly into the area with an own menu entry.

Use the info parameter of the module implementation:
::

    info = dict(area=['admin'], name='modulename', path='modulepath', ...)

This example will add the module 'modulename' in admin area with url `server/admin/modulepath`
"""
from collections import OrderedDict
import flask_login as login
from emonitor.socketserver import SocketHandler
from flask import Blueprint, request, render_template, send_from_directory, current_app, jsonify
from emonitor.decorators import admin_required
from emonitor.user import User
from emonitor.extensions import alembic, babel, signal


admin = Blueprint('admin', __name__, template_folder="web/templates")
admin.modules = OrderedDict()
admin.processes = []  # dict for admin processes


def init_app(app):
    """
    Do all init operations needed for this blueprint

    :param app: :py:class:`Flask` app
    """
    signal.addSignal('admin', 'processes')
    signal.connect('admin', 'processes', adminHandler.handleProcesses)

admin.init_app = init_app


def addModule(module):
    """
    Add module for admin area

    External modules can have a section in the admin area.
    In the init process of the module *addModule()* will be executed to register the module for the admin area

    :param module: :py:class:`emonitor.utils.Module` object
    """
    if module.info['name'] not in admin.modules.keys():
        admin.modules[module.info['name']] = module

admin.addModule = addModule


def addProcess(process):
    """
    The admin area uses processes. External modules can add own *processes* needed for background operations

    :param process: process object
    """
    if process not in admin.processes:
        admin.processes.append(process)
        #signal.send('admin.processes')

admin.addModule = addModule


babel.gettext(u'trigger.default')
babel.gettext(u'trigger.file_added')
babel.gettext(u'trigger.file_removed')
babel.gettext(u'trigger.incoming_serial_data')


@admin.route('/admin')
@admin.route('/admin/')
@admin.route('/admin/<path:module>', methods=['GET', 'POST'])
@admin_required
def adminContent(module=''):
    """
    Admin area is reachable under *http://[servername]:[port]/admin/[module]*

    *module* will execute the *getAdminContent* method of registered module. If no nodule is given, the startpage of
    the admin area will be used

    :param module: module name as string
    :return: rendered HTML-output of module or startpage
    """
    if module == 'upgradedb':  # create new db-revision name given by revisionname
        msg = ""
        if request.args.get('revisionname', '') != '':
            msg = alembic.revision(request.args.get('revisionname'))
        return render_template('admin.dbrevision.html', modules=[], current_mod='upgradedb', user=User.getUsers(login.current_user.get_id() or -1), app_name=current_app.config.get('PROJECT'), app_version=current_app.config.get('APP_VERSION'), path='/admin/' + module, revisionname=request.args.get('revisionname', ''), msg=msg)
    try:
        current_mod = [admin.modules[m] for m in admin.modules if admin.modules[m].info['path'] == module.split('/')[0]][0]
    except IndexError:
        current_mod = admin.modules['startpages']
    return current_mod.getAdminContent(modules=admin.modules, current_mod=current_mod, user=User.getUsers(login.current_user.get_id() or -1), app_name=current_app.config.get('PROJECT'), app_version=current_app.config.get('APP_VERSION'), path='/admin/' + module, help='')


@admin.route('/admin/data/', methods=['GET', 'POST'])
@admin.route('/admin/data/<path:module>', methods=['GET', 'POST'])
def adminData(module=''):
    """
    Admin area is reachable unter *http://[servername]:[port]/admin/data/[module]*

    This path is used to run background operations (e.g. ajax calls) and delivers the result of the `getAdminData`
    method of the module. If **format=json** in the url the result will be formated as json

    :param module: module name as string
    :return: return value of `getAdminData` method of `module`
    """
    current_mod = [admin.modules[m] for m in admin.modules if admin.modules[m].info['path'] == module.split('/')[0]][0]
    result = current_mod.getAdminData()
    if request.args.get('format') == 'json':  # reformat to json
        result = jsonify(result)
        result.status_code = 200
    return result


# static folders
@admin.route('/admin/img/<path:filename>')
def imagebase_static(filename):
    """
    Register url path *http://[servername]:[port]/admin/img/[filename]* for static files

    :param filename: filename as string
    """
    return send_from_directory(admin.root_path + '/web/img/', filename)


@admin.route('/admin/js/<path:filename>')
def jsbase_static(filename):
    """
    Register url path *http://[servername]:[port]/admin/js/[filename]* for static files

    :param filename: filename as string
    """
    return send_from_directory(admin.root_path + '/web/js/', filename)


@admin.route('/admin/css/<path:filename>')
def cssbase_static(filename):
    """
    Register url path *http://[servername]:[port]/admin/css/[filename]* for static files

    :param filename: filename as string
    """
    return send_from_directory(admin.root_path + '/web/css/', filename)


class adminHandler(SocketHandler):
    @staticmethod
    def handleProcesses(sender, **extra):
        """
        Handler for background processes

        :param sender: operation class or module
        :param extra: parameters of process as dict list
        """
        if 'id' in extra:  # TODO CHANGE PROCESS INFO
            SocketHandler.send_message(str(extra['id']))
        else:
            SocketHandler.send_message('admin.processes', **extra)
