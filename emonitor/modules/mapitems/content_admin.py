import os, imp
from flask import render_template, request, current_app
from emonitor.extensions import db, babel, scheduler
from emonitor.utils import Pagination
from emonitor.modules.mapitems.mapitem import MapItem, ItemLayout
from emonitor.modules.settings.settings import Settings
from emonitor.modules.streets.city import City

PER_PAGE = 25


def getAdminContent(self, **params):
    """
    Deliver admin content of module mapitems

    :param params: use given parameters of request
    :return: rendered template as string
    """
    module = request.view_args['module'].split('/')
    if len(module) < 2:
        module.append(current_app.blueprints['admin'].modules['mapitems'].adminsubnavigation[0][0].split('/')[-1])  # get first submenuitem

    if len(module) >= 2:
        if module[1] == 'definition':  # definition
            if request.method == 'POST':

                if request.form.get('action').startswith('edititemtype_'):  # edit/add definition TODO: fix
                    typename = request.form.get('action').split('_')
                    itemtype = [d for d in Settings.get('mapitemdefinition') if d['name'] == typename[1]]
                    if len(itemtype) > 0:
                        itemtype = itemtype[0]
                        if 'parameters' not in itemtype:
                            itemtype['parameters'] = {'layout': '', 'tileserver': 0}
                        if 'key' not in itemtype:
                            itemtype['key'] = []
                        if 'cities' not in itemtype:
                            itemtype['cities'] = []
                        if 'itemtype' not in itemtype:
                            itemtype['itemtype'] = 'node'
                    else:
                        itemtype = {'name': '', 'filter': '', 'attributes': [], 'parameters': {'layout', 'tileserver'}, 'key': [], 'cities': [], 'itemtype': 'node'}
                    params.update({'itemtype': itemtype, 'cities': City.getCities(), 'layouters': MapItem.getLayouters()})
                    return render_template('admin.mapitems.definition_actions.html', **params)

                elif request.form.get('action').startswith('deleteitemtype_'):  # delete definition
                    itemtypes = Settings.get('mapitemdefinition')
                    for itemtype in itemtypes:
                        if itemtype['name'] == request.form.get('action').split('_')[1]:
                            del itemtypes[itemtypes.index(itemtype)]
                    Settings.set('mapitemdefinition', itemtypes)
                    db.session.commit()

                elif request.form.get('action') == 'updateitemtypes':  # save definition
                    itemtypes = Settings.get('mapitemdefinition')
                    position = -1
                    for itemtype in itemtypes:
                        if itemtype['name'] == request.form.get('edit_name'):
                            position = itemtypes.index(itemtype)
                            break
                    if position >= 0:  # update type
                        itemtypes[position]['filter'] = request.form.get('edit_filter')
                        itemtypes[position]['cities'] = [int(i) for i in request.form.getlist('edit_cityid')]
                        itemtypes[position]['itemtype'] = request.form.get('edit_itemtype')
                        itemtypes[position]['attributes'] = request.form.get('edit_attributes').split('\r\n')
                        itemtypes[position]['parameters'] = {'layout': request.form.get('edit_layout'), 'tileserver': request.form.get('edit_tileserver')}
                        itemtypes[position]['key'] = request.form.get('edit_keys').split('\r\n')

                    else:  # add new type
                        it = dict()
                        it['name'] = request.form.get('edit_name')
                        it['filter'] = request.form.get('edit_filter')
                        it['cities'] = [int(i) for i in request.form.getlist('edit_cityid')]
                        it['itemtype'] = request.form.get('edit_itemtype')
                        it['attributes'] = request.form.get('edit_attributes').split('\r\n')
                        it['parameters'] = {'layout': request.form.get('edit_layout')}
                        if itemtypes == "":
                            itemtypes = [it]
                        else:
                            itemtypes.append(it)
                        it['key'] = request.form.get('edit_keys').split('\r\n')
                    Settings.set('mapitemdefinition', itemtypes)
                    db.session.commit()
                    current_app.blueprints['admin'].modules['mapitems'].updateAdminSubNavigation()

            params.update({'itemtypes': Settings.get('mapitemdefinition', []), 'layouters': MapItem.getLayouters()})
            return render_template('admin.mapitems.definition.html', **params)

    # deliver default list
    itemdefinition = [t for t in Settings.get('mapitemdefinition') if t['name'] == module[1]][0]
    itemtypes = MapItem.getMapitems(itemtype=module[1])
    page = 0
    if len(module) == 3:  # pagination active
        page = int(module[2])
    pagination = Pagination(page, PER_PAGE, len(itemtypes))

    params.update({'itemtypes': itemtypes[page:page + PER_PAGE], 'itemdefinition': itemdefinition, 'pagination': pagination})
    return render_template('admin.mapitems.html', **params)


def getAdminData(self):
    """
    Deliver admin content of module mapitems (ajax)

    :return: rendered template as string or json dict
    """
    if request.args.get('action') == 'loadfromosm':  # load all objects from osm
        itemdefinition = [t for t in Settings.get('mapitemdefinition') if t['name'] == request.args.get('type')][0]
        dbodmids = [int(i.osmid) for i in MapItem.getMapitems(itemtype=itemdefinition['name'])]

        for cid in itemdefinition['cities']:
            city = City.getCities(id=cid)
            for item in MapItem.loadFromOSM(itemdefinition, city.name):
                if int(item['id']) > 0 and int(item['id']) not in dbodmids:  # add item
                    attrs = item.copy()
                    del attrs['id']
                    db.session.add(MapItem(itemdefinition['name'], int(item['id']), attrs))
                else:  # update
                    pass  # TODO write update method

        db.session.commit()

    elif request.args.get('action') == 'uploadlayouter':
        if request.files:
            ufile = request.files['uploadfile']
            if not os.path.exists('%s/emonitor/modules/alarms/inc/%s' % (current_app.config.get('PROJECT_ROOT'), ufile.filename)):
                ufile.save('%s/emonitor/modules/mapitems/inc/%s' % (current_app.config.get('PROJECT_ROOT'), ufile.filename))
                try:
                    cls = imp.load_source('emonitor.modules.mapitems.inc', 'emonitor/modules/mapitems/inc/%s' % ufile.filename)
                    if isinstance(getattr(cls, cls.__all__[0])(), ItemLayout):
                        return "ok"
                except:
                    pass
                os.remove('%s/emonitor/modules/mapitems/inc/%s' % (current_app.config.get('PROJECT_ROOT'), ufile.filename))
                return babel.gettext(u'admin.mapitems.layouternotvalid')
        return ""

    elif request.args.get('action') == 'buildtiles':
        itemdefinition = [t for t in Settings.get('mapitemdefinition') if t['name'] == request.args.get('type')][0]
        for layouter in MapItem.getLayouters():
            if layouter.getName() == itemdefinition['parameters']['layout']:
                scheduler.add_job(layouter.buildTiles, args=[MapItem.getMapitems(itemdefinition['name']), itemdefinition['attributes']])
                break

    return ""
