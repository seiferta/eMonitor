from collections import OrderedDict
import flask.ext.login as login
from emonitor.sockethandler import SocketHandler
from flask import Blueprint, request, send_from_directory, current_app, jsonify
from emonitor.decorators import admin_required
from emonitor.user import User
from emonitor.extensions import babel, signal


admin = Blueprint('admin', __name__, template_folder="web/templates")
admin.modules = OrderedDict()
admin.processes = []  # dict for admin processes


def init_app(app):
    signal.addSignal('admin', 'processes')
    signal.connect('admin', 'processes', adminHandler.handleProcesses)

admin.init_app = init_app


def addModule(module):
    if module.info['name'] not in admin.modules.keys():
        admin.modules[module.info['name']] = module

admin.addModule = addModule


def addProcess(process):
    if process not in admin.processes:
        admin.processes.append(process)
        #signal.send('admin.processes')

admin.addModule = addModule


babel.gettext(u'trigger.default')
babel.gettext(u'trigger.file_added')
babel.gettext(u'trigger.file_removed')


@admin.route('/admin')
@admin.route('/admin/')
@admin.route('/admin/<path:module>', methods=['GET', 'POST'])
@admin_required
def adminContent(module=''):
    try:
        current_mod = [admin.modules[m] for m in admin.modules if admin.modules[m].info['path'] == module.split('/')[0]][0]
    except IndexError:
        current_mod = admin.modules['startpages']
        current_app.logger.error("admin module %s not found" % module)
    return current_mod.getAdminContent(modules=admin.modules, current_mod=current_mod, user=User.getUsers(login.current_user.get_id() or -1), app_name=current_app.config.get('PROJECT'), app_version=current_app.config.get('APP_VERSION'), path='/admin/' + module)


@admin.route('/admin/data/', methods=['GET', 'POST'])
@admin.route('/admin/data/<path:module>', methods=['GET', 'POST'])
def adminData(module=''):
    current_mod = [admin.modules[m] for m in admin.modules if admin.modules[m].info['path'] == module.split('/')[0]][0]
    result = current_mod.getAdminData()
    if request.args.get('format') == 'json':  # reformat to json
        result = jsonify(result)
        result.status_code = 200
    return result


# static folders
@admin.route('/admin/img/<path:filename>')
def imagebase_static(filename):
    return send_from_directory(admin.root_path + '/web/img/', filename)


@admin.route('/admin/js/<path:filename>')
def jsbase_static(filename):
    return send_from_directory(admin.root_path + '/web/js/', filename)


@admin.route('/admin/css/<path:filename>')
def cssbase_static(filename):
    return send_from_directory(admin.root_path + '/web/css/', filename)


class adminHandler(SocketHandler):
    @staticmethod
    def handleProcesses(sender, **extra):
        # TODO: change process info
        print "EXTRAS;", extra

        if 'id' in extra:
            SocketHandler.send_message(str(extra['id']))
        else:
            SocketHandler.send_message('admin.processes', **extra)