from flask import render_template, request
from emonitor.modules.maps.map import Map
from emonitor.modules.mapitems.mapitem import MapItem
from emonitor.modules.settings.settings import Settings


def getFrontendContent(**params):
    """
    Deliver frontend content of module maps

    :return: data of maps
    """
    if 'area' not in params.keys() and request.args.get('area', '') != '':
        params['area'] = request.args.get('area')

    if 'area' in params.keys() and params['area'] in ['west', 'center', 'east']:  # select view
        tiledefs = [d for d in Settings.get('mapitemdefinition') if d['parameters']['tileserver'] == '1']

        return render_template('frontend.map.html', maps=Map.getMaps(), defaultlat=Settings.get('defaultLat'), defaultlng=Settings.get('defaultLng'), defaultzoom=Settings.get('defaultZoom'), maptype="" or Map.getDefaultMap(), tiledefs=tiledefs)
    return "default"


def getFrontendData(self):
    """
    Deliver frontend content of module maps (ajax)

    :return: rendered template as string or json dict
    """
    if 'action' in request.args:
        if request.args.get('action') == 'mapitems':
            return MapItem.getMapitems(itemtype=request.args.get('itemtype'))[:3]

    return ""
