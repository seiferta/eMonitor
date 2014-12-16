from collections import OrderedDict
import codecs
from flask import Blueprint, current_app, render_template, send_from_directory

from emonitor.extensions import babel
import emonitor.admin.admin as admin

onlinehelp = Blueprint('onlinehelp', __name__, template_folder="web/templates")
onlinehelp.modules = OrderedDict()

babel.gettext(u'emonitor.monitorserver.MonitorServer')
babel.gettext(u'trigger.default')


def _addModule(module):
    if module.info['name'] not in onlinehelp.modules.keys():
        onlinehelp.modules[module.info['name']] = module

onlinehelp.addModule = _addModule


@onlinehelp.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_from_directory(onlinehelp.root_path + '/web/img/', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@onlinehelp.route('/help/', methods=['GET', 'POST'])
@onlinehelp.route('/help/<path:module>', methods=['GET', 'POST'])
def helpContent(module=u''):
    helpcontent = ''
    index = []
    path = module
    if module.startswith('admin'):  # admin area
        area = "admin"
        module = ".".join(module.split('/')[1:])

    elif module.startswith('frontend'):  # frontend area
        area = "frontend"
        module = ".".join(module.split('/')[1:])
    else:
        area = ""
        module = ""

    try:
        if module.split('.')[0] in current_app.blueprints[area].modules.keys():  # load module help text
            helpcontent = current_app.blueprints[area].modules[module.split('.')[0]].getHelp(area=area, name=module)

        if helpcontent == '':  # use default content + index
            with codecs.open('%s/web/templates/%s.de.default.rst' % (onlinehelp.root_path, area), 'r', encoding="utf-8") as content:
                helpcontent = content.read()
            # load index
            index = [m for m in admin.admin.modules.values()if m.hasHelp('admin')]
        return render_template('onlinehelp.html', helpcontent=helpcontent, index=index)
    except KeyError:
        if '.' not in path:
            path += 'index.html'
        return send_from_directory("%s/docs/output/html/" % current_app.config.get('PROJECT_ROOT'), path)


# static folders
@onlinehelp.route('/help/img/<path:filename>')
def imageonlinehelpbase_static(filename):
    return send_from_directory(onlinehelp.root_path + '/web/img/', filename)


@onlinehelp.route('/help/js/<path:filename>')
def jsonlinehelpbase_static(filename):
    return send_from_directory(onlinehelp.root_path + '/web/js/', filename)


@onlinehelp.route('/help/css/<path:filename>')
def cssonlinehelpbase_static(filename):
    return send_from_directory(onlinehelp.root_path + '/web/css/', filename)
