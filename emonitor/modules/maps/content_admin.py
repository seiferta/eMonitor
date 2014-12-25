import os
from flask import request, render_template, current_app

from emonitor.extensions import classes, db, babel
from emonitor.modules.maps.map import Map
import map_utils

OBSERVERACTIVE = 1


def getAdminContent(self, **params):
    """
    Deliver admin content of module maps

    :param params: use given parameters of request
    :return: rendered template as string
    """
    module = request.view_args['module'].split('/')

    if len(module) > 1:
        if module[1] == 'position':
            if request.method == 'POST':
                if request.form.get('action') == 'saveposition':  # safe default map position and home position
                    classes.get('settings').set('defaultLat', request.form.get('default_lat', ''))
                    classes.get('settings').set('defaultLng', request.form.get('default_lng', ''))
                    classes.get('settings').set('defaultZoom', request.form.get('default_zoom', ''))

                    classes.get('settings').set('homeLat', request.form.get('home_lat', ''))
                    classes.get('settings').set('homeLng', request.form.get('home_lng', ''))

                    db.session.commit()

            params.update({'settings': classes.get('settings')})
            return render_template('admin.map.position.html', **params)

    else:
        if request.method == 'POST':
            if request.form.get('action') == 'savemap':  # save map
                if request.form.get('map_id') != 'None':  # update
                    _map = classes.get('map').getMaps(request.form.get('map_id'))
                    _map.name = request.form.get('map_name')
                    _map.path = request.form.get('map_path')
                    _map.maptype = int(request.form.get('map_type'))
                    _map.tileserver = request.form.get('map_tileserver')
                    _map.default = request.form.get('map_default')
                else:  # add map
                    _map = Map(request.form.get('map_name'), request.form.get('map_path'), int(request.form.get('map_type')), request.form.get('map_tileserver'), int(request.form.get('map_default')))
                    db.session.add(_map)
                db.session.commit()

            elif request.form.get('action') == 'createmap':  # add map
                params.update({'map': Map('', '', 0, '', 0), 'progress': map_utils.LOADINPROGRESS, 'tilebase': current_app.config.get('PATH_TILES'), 'settings': classes.get('settings')})
                return render_template('admin.map_actions.html', **params)

            elif request.form.get('action').startswith('detailmap_'):  # edit map
                params.update({'map': Map.getMaps(request.form.get('action').split('_')[-1]), 'settings': classes.get('settings'), 'tilebase': current_app.config.get('PATH_TILES'), 'progress': map_utils.LOADINPROGRESS, 'tiles': '\', \''.join(classes.get('settings').getMapTiles(int(request.form.get('action').split('_')[-1])))})
                return render_template('admin.map_actions.html', **params)

            elif request.form.get('action').startswith('deletemap_'):  # delete map
                db.session.delete(Map.getMaps(int(request.form.get('action').split('_')[-1])))
                db.session.commit()

            elif request.form.get('action') == 'ordersetting':  # change map order
                maps = []
                for _id in request.form.getlist('mapids'):
                    _map = Map.getMaps(int(_id))
                    maps.append(dict(name=_map.__dict__['name'], path=_map.__dict__['path'], maptype=_map.__dict__['maptype'], tileserver=_map.__dict__['tileserver'], default=_map.__dict__['default']))
                db.session.query(Map).delete()  # delete all maps
                for _map in maps:  # add maps in new order
                    db.session.add(Map(_map['name'], _map['path'], _map['maptype'], _map['tileserver'], _map['default']))
                db.session.commit()

    params.update({'maps': classes.get('map').getMaps()})
    return render_template('admin.map.html', **params)


def getAdminData(self, **params):
    """
    Deliver admin content of module maps (ajax)

    :return: rendered template as string or json dict
    """
    if request.args.get('action') == 'checkpath':
        if os.path.exists(request.args.get('path')):
            return '1'
        return '0'

    elif request.args.get('action') == 'loadmap':  # load tiles

        tile_path = request.args.get('path')

        def calcSubItems((pos)):
            return [(2 * int(pos[0]), 2 * int(pos[1])), (2 * int(pos[0]) + 1, 2 * int(pos[1])), (2 * int(pos[0]), 2 * int(pos[1]) + 1), (2 * int(pos[0]) + 1, 2 * int(pos[1]) + 1)]

        #def getTile(zoom, pos):
        #    global tile_path
        #    response = urllib2.urlopen('http://a.tile.openstreetmap.org/%s/%s/%s.png' % (zoom, pos[0], pos[1]))
        #    #fout = open(tile_path + str(zoom)+'/'+str(pos[0])+'-'+str(pos[1])+'.png', 'wb')
        #    fout = open("%s%s/%s-%s.png" % (tile_path, zoom, pos[0], pos[1]), 'wb')
        #    fout.write(response.read())
        #    fout.close()

        _items = {12: [], 13: [], 14: [], 15: [], 16: [], 17: [], 18: []}
        for t in request.args.get('tiles').split("-"):
            if t != '':
                _items[12].append(t.split(","))

        for zoom in range(13, 19):
            for i in _items[zoom - 1]:
                _items[zoom] += calcSubItems(i)

        result = map_utils.loadTiles('%s%s' % (current_app.config.get('PATH_TILES'), request.args.get('path')), _items)
        if result == 0:
            return babel.gettext('settings.map.loadinginprogress')  # loading still active
        elif result == 1:
            return babel.gettext('settings.map.loadingstarted')  # loading started
        return ""

    elif request.args.get('action') == 'tileprogress':
        return {'position': map_utils.LOADINPROGRESS[1], 'of': map_utils.LOADINPROGRESS[0]}

    elif request.args.get('action') == 'maptiles':
        _map = classes.get('map').getMaps(id=request.args.get('id'))
        if _map:
            return classes.get('map').getMapBox(tilepath=current_app.config.get('PATH_TILES'), mappath=_map.path)
        return classes.get('map').getMapBox()

    elif request.args.get('action') == 'loadosmdata':  # load all data from openstreetmap
        from emonitor.extensions import scheduler
        from emonitor.lib.osm.loaddata import parseOsmData
        #import time, datetime
        mapdata = classes.get('map').getMaps()[0].getMapBox(tilepath=current_app.config.get('PATH_TILES'))

        lat = [mapdata['min_latdeg']]
        while lat[-1] + .05 < mapdata['max_latdeg']:
            lat.append(lat[-1] + .05)
        lat.append(mapdata['max_latdeg'])

        lng = [mapdata['min_lngdeg']]
        while lng[-1] + .05 < mapdata['max_lngdeg']:
            lng.append(lng[-1] + .05)
        lng.append(mapdata['max_lngdeg'])

        scheduler.add_job(parseOsmData, kwargs={'lat': lat, 'lng': lng, 'path': current_app.config.get('PATH_DATA')})
        return {'job': 'started'}

    elif request.args.get('action') == 'findcity':  # search citystring and deliver position
        return map_utils.loadPositionOfCity(request.args.get('cityname'))

    return ""
