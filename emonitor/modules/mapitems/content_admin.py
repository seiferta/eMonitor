from flask import render_template, request, current_app
from emonitor.extensions import classes, db, scheduler
from emonitor.utils import Pagination
from mapitem import MapItem
from mapitem_utils import buildTiles

PER_PAGE = 25


def getAdminContent(self, **params):

    module = request.view_args['module'].split('/')
    if len(module) < 2:
        module.append(current_app.blueprints['admin'].modules['mapitems'].adminsubnavigation[0][0].split('/')[-1])  # get first submenuitem

    if len(module) >= 2:
        if module[1] == 'definition':  # definition
            if request.method == 'POST':

                if request.form.get('action').startswith('edititemtype_'):  # edit/add definition TODO: fix
                    typename = request.form.get('action').split('_')
                    itemtype = [d for d in classes.get('settings').get('mapitemdefinition') if d['name'] == typename[1]]
                    if len(itemtype) > 0:
                        itemtype = itemtype[0]
                        if not 'parameters' in itemtype:
                            itemtype['parameters'] = {'layout': '', 'tileserver': 0}
                        if not 'key' in itemtype:
                            itemtype['key'] = []
                    else:
                        itemtype = {'name': '', 'filter': '', 'attributes': [], 'parameters': {'layout', 'tileserver'}, 'key': []}
                    params.update({'itemtype': itemtype})
                    return render_template('admin.mapitems.definition_actions.html', **params)

                elif request.form.get('action').startswith('deleteitemtype_'):  # delete definition
                    itemtypes = classes.get('settings').get('mapitemdefinition')
                    for itemtype in itemtypes:
                        if itemtype['name'] == request.form.get('action').split('_')[1]:
                            del itemtypes[itemtypes.index(itemtype)]
                    classes.get('settings').set('mapitemdefinition', itemtypes)
                    db.session.commit()

                elif request.form.get('action') == 'updateitemtypes':  # save definition
                    itemtypes = classes.get('settings').get('mapitemdefinition')
                    position = -1
                    for itemtype in itemtypes:
                        if itemtype['name'] == request.form.get('edit_name'):
                            position = itemtypes.index(itemtype)
                            break
                    if position >= 0:  # update type
                        itemtypes[position]['filter'] = request.form.get('edit_filter')
                        itemtypes[position]['attributes'] = request.form.get('edit_attributes').split('\r\n')
                        itemtypes[position]['parameters'] = {'layout': request.form.get('edit_layout'), 'tileserver': request.form.get('edit_tileserver')}
                        itemtypes[position]['key'] = request.form.get('edit_keys').split('\r\n')

                    else:  # add new type
                        it = dict()
                        it['name'] = request.form.get('edit_name')
                        it['filter'] = request.form.get('edit_filter')
                        it['attributes'] = request.form.get('edit_attributes').split('\r\n')
                        it['parameters'] = {'layout': request.form.get('edit_layout')}
                        if itemtypes == "":
                            itemtypes = [it]
                        else:
                            itemtypes.append(it)
                        it['key'] = request.form.get('edit_keys').split('\r\n')
                    classes.get('settings').set('mapitemdefinition', itemtypes)
                    db.session.commit()
                    current_app.blueprints['admin'].modules['mapitems'].updateAdminSubNavigation()

            params.update({'itemtypes': classes.get('settings').get('mapitemdefinition', [])})
            return render_template('admin.mapitems.definition.html', **params)

    # deliver default list
    itemdefinition = [t for t in classes.get('settings').get('mapitemdefinition') if t['name'] == module[1]][0]
    itemtypes = MapItem.getMapitems(itemtype=module[1])
    page = 0
    if len(module) == 3:  # pagination active
        page = int(module[2])
    pagination = Pagination(page, PER_PAGE, len(itemtypes))

    params.update({'itemtypes': itemtypes[page:page + PER_PAGE], 'itemdefinition': itemdefinition, 'pagination': pagination})
    return render_template('admin.mapitems.html', **params)


def getAdminData(self):
    if request.args.get('action') == 'loadfromosm':  # load all objects from osm
        map_details = classes.get('map').getMaps()[0].getMapBox(tilepath=current_app.config.get('PATH_TILES'))
        itemdefinition = [t for t in classes.get('settings').get('mapitemdefinition') if t['name'] == request.args.get('type')][0]
        dbodmids = [int(i.osmid) for i in MapItem.getMapitems(itemtype=itemdefinition['name'])]

        for item in classes.get('mapitem').loadFromOSM(itemdefinition, map_details):
            if int(item['id']) > 0 and int(item['id']) not in dbodmids:  # add item
                attrs = item.copy()
                del attrs['id']
                db.session.add(MapItem(itemdefinition['name'], int(item['id']), attrs))
            else:  # update
                pass  # TODO write update method

        db.session.commit()

    elif request.args.get('action') == 'buildtiles':
        itemdefinition = [t for t in classes.get('settings').get('mapitemdefinition') if t['name'] == request.args.get('type')][0]
        scheduler.add_single_job(buildTiles, [itemdefinition, [16, 17, 18]])

    return ""