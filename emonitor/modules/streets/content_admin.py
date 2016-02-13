from flask import request, render_template, flash

from emonitor.extensions import db, cache, scheduler, babel
from emonitor.modules.streets.city_utils import loadCitiesFromOsm
from emonitor.modules.streets.street_utils import loadStreetsFromOsm
from emonitor.modules.streets.housenumber_utils import loadHousenumbersFromOsm
from emonitor.modules.streets.street import Street
from emonitor.modules.streets.housenumber import Housenumber
from emonitor.modules.streets.city import City
from emonitor.modules.settings.department import Department
from emonitor.modules.maps.map import Map
from emonitor.modules.settings.settings import Settings


def getAdminContent(self, **params):
    """
    Deliver admin content of module streets

    :param params: use given parameters of request
    :return: rendered template as string
    """
    module = request.view_args['module'].split('/')
    if len(module) < 2:
        if City.getDefaultCity():
            module.append(u'{}'.format(City.getDefaultCity().id))
        else:
            module.append(u'1')

    if len(module) == 2:  # cities
        if module[1] == '0':  # city list

            if request.method == 'POST':

                if request.form.get('action').startswith('detailcity_'):  # edit city
                    params.update({'city': City.getCities(id=request.form.get('action').split('_')[-1]), 'departments': Department.getDepartments(), 'maps': Map.getMaps()})
                    return render_template('admin.streets.city_edit.html', **params)

                elif request.form.get('action') == 'updatecity':  # update existing city
                    if request.form.get('city_id') != 'None':  # update city
                        city = City.getCities(id=request.form.get('city_id'))
                        city.name = request.form.get('cityname')
                        city.subcity = request.form.get('subcity')
                        city._dept = request.form.get('department')
                        city.mapname = request.form.get('citymap')
                        city.color = request.form.get('colorname')
                        city.default = request.form.get('citydefault')
                        city.osmid = request.form.get('osmid')
                        city.osmname = request.form.get('osmname')

                    else:  # add city
                        city = City(request.form.get('cityname'), request.form.get('department'),
                                    request.form.get('citymap'), request.form.get('citydefault'),
                                    request.form.get('subcity'), request.form.get('colorname'),
                                    request.form.get('osmid'), request.form.get('osmname'))
                        db.session.add(city)

                    db.session.commit()
                    cache.clear()

                elif request.form.get('action') == 'createcity':  # add city
                    params.update({'city': City('', '', '', '', '', '', 0, ''), 'departments': Department.getDepartments(), 'maps': Map.getMaps()})
                    return render_template('admin.streets.city_edit.html', **params)

                elif request.form.get('action').startswith('deletecity_'):  # delete city
                    db.session.delete(City.getCities(id=request.form.get('action').split('_')[-1]))
                    db.session.commit()
                self.updateAdminSubNavigation()
                cache.clear()

            params.update({'cities': City.getCities()})
            return render_template('admin.streets.city_list.html', **params)

        else:  # show city details
            if request.method == 'POST':
                if request.form.get('action').startswith('detailstreet_'):  # edit street
                    tileserver = {'lat': Settings.get('defaultLat'),
                                  'lng': Settings.get('defaultLng'),
                                  'zoom': Settings.get('defaultZoom'),
                                  'map': Map.getDefaultMap()}
                    params.update({'street': Street.getStreets(id=request.form.get('action').split('_')[-1]), 'cities': City.getCities(), 'maps': Map.getMaps(), 'tileserver': tileserver})
                    return render_template('admin.streets_edit.html', **params)

                elif request.form.get('action') == 'createstreet':  # add street
                    tileserver = {'lat': Settings.get('defaultLat'),
                                  'lng': Settings.get('defaultLng'),
                                  'zoom': Settings.get('defaultZoom'),
                                  'map': Map.getDefaultMap()}

                    params.update({'street': Street('', '', int(module[1]), '', '', '', '', '', ''), 'cities': City.getCities(), 'maps': Map.getMaps(), 'tileserver': tileserver})
                    return render_template('admin.streets_edit.html', **params)

                elif request.form.get('action').startswith('deletestreets_'):  # delete street
                    db.session.delete(Street.getStreets(id=request.form.get('action').split('_')[-1]))
                    db.session.commit()
                    cache.clear()

                elif request.form.get('action') == 'savestreet':  # save street
                    if request.form.get('street_id') != 'None':  # update existing street
                        street = Street.getStreets(id=request.form.get('street_id'))
                        street.name = request.form.get('edit_name')
                        street.navigation = request.form.get('edit_navigation')
                        c = request.form.get('edit_cityid').split('_')
                        if len(c) < 2:
                            c.append('')
                        street.cityid = c[0]
                        street.subcity = c[1]
                        street.lat = request.form.get('edit_lat')
                        street.lng = request.form.get('edit_lng')
                        street.zoom = request.form.get('edit_zoom')
                        street.active = request.form.get('edit_active')
                        db.session.commit()
                        #cache.delete_memoized(City.streets)

                    else:  # add street
                        c = request.form.get('edit_cityid').split('_')
                        if len(c) < 2:
                            c.append('')  # subcity
                        city = [ct for ct in City.getCities() if str(ct.id) == c[0]][0]
                        city.addStreet(Street(request.form.get('edit_name'), request.form.get('edit_navigation'), int(c[0]), c[1], request.form.get('edit_lat'), request.form.get('edit_lng'), request.form.get('edit_zoom'), request.form.get('edit_active'), 0))
                        db.session.commit()
                    cache.clear()

            try:
                streets = Street.getStreets(cityid=module[-1])
            except AttributeError:
                streets = []
            chars = {}
            for s in streets:
                chars[s.name[0].upper()] = 0
            params.update({'streets': streets, 'chars': sorted(chars.keys()), 'city': City.getCities(id=module[-1])})
            return render_template('admin.streets.html', **params)

    return "streets"


def getAdminData(self):
    """
    Deliver admin content of module streets (ajax)

    :return: rendered template as string or json dict
    """
    if request.args.get('action') == 'loadcitiesfromosm':  # get city list from osm
        return loadCitiesFromOsm()

    elif request.args.get('action') == 'createcity':  # create cities from osm
        osmids = [c[0] for c in db.get(City.osmid).all()]
        i = 0
        for c in request.args.get('values').split(","):
            _id, name = c.split('|')
            if int(_id) not in osmids:  # add city
                db.session.add(City(name, 1, '', 0, '', '', int(_id), ''))
                db.session.commit()
                i += 1

        flash(babel.gettext('%(i)s admin.streets.cities.osmcitiesadded', i=i))
        self.updateAdminSubNavigation()
        return '1'

    elif request.args.get('action') == 'loadstreetsfromosm':  # get street list from osm
        return loadStreetsFromOsm(City.getCities(id=request.args.get('cityid')))

    elif request.args.get('action') == 'createstreet':  # create streets from osm
        city = City.getCities(id=request.args.get('cityid'))
        ids = [int(i) for i in request.args.get('values').split(",")]  # ids to create
        osmdata = loadStreetsFromOsm(city=city, format='data')

        i = 0
        for sname in osmdata:
            if len(set(osmdata[sname]['osmids']).intersection(set(ids))) > 0:  # add street
                _s = osmdata[sname]
                city.addStreet(
                    Street(sname, '', int(request.args.get('cityid')), '', _s['center'][0], _s['center'][1], 17, 1,
                           _s['osmids'][0]))
                i += 1
        flash(babel.gettext('%(i)s admin.streets.osmstreetsadded', i=i))
        return '1'

    elif request.args.get('action') == 'loadhnumbersfromosm':
        if 'streetid' in request.args:
            streets = [Street.getStreets(id=int(request.args.get('streetid')))]
        elif 'cityid' in request.args:
            #streets = list(City.getCities(id=request.args.get('cityid')).streets)
            streets = Street.getStreets(cityid=int(request.args.get('cityid')))
        else:
            streets = Street.getStreets()
        return str(scheduler.add_job(loadHousenumbersFromOsm, args=[streets]))

    elif request.args.get('action') == 'loadhnumbers':  # load all housenumbers for street
        street = Street.getStreets(id=request.args.get('streetid'))
        ret = dict()
        for hn in street.housenumbers:
            ret[hn.id] = hn.points
        return ret

    elif request.args.get('action') == 'delhousenumber':  # delete housenumber
        hn = Housenumber.getHousenumbers(id=request.args.get('housenumberid'))
        street = hn.street
        db.session.delete(hn)
        db.session.commit()
        return render_template('admin.streets.housenumber.html', hnumbers=street.housenumbers)

    elif request.args.get('action') == 'addhousenumber':  # add housenumber
        street = Street.getStreets(id=request.args.get('streetid'))
        points = []
        p = request.args.get('points').split(';')
        points.append((float(p[0]), float(p[1])))
        street.addHouseNumber(request.args.get('hnumber'), points)
        return render_template('admin.streets.housenumber.html', hnumbers=street.housenumbers)

    return "NONE"
