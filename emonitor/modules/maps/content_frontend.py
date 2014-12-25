from flask import render_template, request
from emonitor.extensions import classes
from emonitor.modules.maps.map import Map


def getFrontendContent(**params):
    """
    Deliver frontend content of module maps

    :return: data of maps
    """
    if 'area' not in params.keys() and request.args.get('area', '') != '':
        params['area'] = request.args.get('area')

    if 'area' in params.keys() and params['area'] in ['west', 'center', 'east']:  # select view
        tiledefs = [d for d in classes.get('settings').get('mapitemdefinition') if d['parameters']['tileserver'] == '1']

        return render_template('frontend.map.html', maps=Map.getMaps(), defaultlat=classes.get('settings').get('defaultLat'), defaultlng=classes.get('settings').get('defaultLng'), defaultzoom=classes.get('settings').get('defaultZoom'), maptype=Map.getDefaultMap().name, tiledefs=tiledefs)
    return "default"


def getFrontendData(self):
    """
    Deliver frontend content of module maps (ajax)

    :return: rendered template as string or json dict
    """
    if 'action' in request.args:
        if request.args.get('action') == 'mapitems':
            return classes.get('mapitem').getMapitems(itemtype=request.args.get('itemtype'))[:3]

    return ""
