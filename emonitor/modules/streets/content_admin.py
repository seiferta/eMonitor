from flask import request, render_template, flash

from emonitor.extensions import classes, db, cache, scheduler, babel
from .city_utils import loadCitiesFromOsm
from .street_utils import loadStreetsFromOsm
from .housenumber_utils import loadHousenumbersFromOsm
from emonitor.modules.streets.street import Street
from emonitor.modules.streets.city import City


def getAdminContent(self, **params):
    module = request.view_args['module'].split('/')
    if len(module) < 2:
        if classes.get('city').getDefaultCity():
            module.append(u'%s' % classes.get('city').getDefaultCity().id)
        else:
            module.append(u'1')

    if len(module) == 2:  # cities
        if module[1] == '0':  # city list

            if request.method == 'POST':

                if request.form.get('action').startswith('detailcity_'):  # edit city
                    params.update({'city': classes.get('city').get_byid(int(request.form.get('action').split('_')[-1])), 'departments': classes.get('department').getDepartments(), 'maps': classes.get('map').getMaps()})
                    return render_template('admin.streets.city_edit.html', **params)

                elif request.form.get('action') == 'updatecity':  # update existing city
                    if request.form.get('city_id') != 'None':  # update city
                        city = classes.get('city').get_byid(int(request.form.get('city_id')))
                        city.name = request.form.get('cityname')
                        city.subcity = request.form.get('subcity')
                        city._dept = request.form.get('department')
                        city.mapname = request.form.get('citymap')
                        city.color = request.form.get('colorname')
                        city.default = request.form.get('citydefault')
                        city.osmid = request.form.get('osmid')
                        city.osmname = request.form.get('osmname')

                    else:  # add city
                        city = classes.get('city')(request.form.get('cityname'), request.form.get('department'),
                                                   request.form.get('citymap'), request.form.get('citydefault'),
                                                   request.form.get('subcity'), request.form.get('colorname'),
                                                   request.form.get('osmid'), request.form.get('osmname'))
                        db.session.add(city)

                    db.session.commit()
                    cache.clear()

                elif request.form.get('action') == 'createcity':  # add city
                    params.update({'city': classes.get('city')('', '', '', '', '', '', 0, ''), 'departments': classes.get('department').getDepartments(), 'maps': classes.get('map').getMaps()})
                    return render_template('admin.streets.city_edit.html', **params)

                elif request.form.get('action').startswith('deletecity_'):  # delete city
                    db.session.delete(classes.get('city').get_byid(request.form.get('action').split('_')[-1]))
                    db.session.commit()
                self.updateAdminSubNavigation()
                cache.clear()

            params.update({'cities': classes.get('city').getCities()})
            return render_template('admin.streets.city_list.html', **params)

        else:  # show city details
            if request.method == 'POST':
                if request.form.get('action').startswith('detailstreet_'):  # edit street
                    tileserver = {'lat': classes.get('settings').get('defaultLat'),
                                  'lng': classes.get('settings').get('defaultLng'),
                                  'zoom': classes.get('settings').get('defaultZoom'),
                                  'map': classes.get('map').getDefaultMap()}
                    params.update({'street': classes.get('street').getStreet(id=request.form.get('action').split('_')[-1]), 'cities': classes.get('city').getCities(), 'maps': classes.get('map').getMaps(), 'tileserver': tileserver})
                    return render_template('admin.streets_edit.html', **params)

                elif request.form.get('action') == 'createstreet':  # add street
                    tileserver = {'lat': classes.get('settings').get('defaultLat'),
                                  'lng': classes.get('settings').get('defaultLng'),
                                  'zoom': classes.get('settings').get('defaultZoom'),
                                  'map': classes.get('map').getDefaultMap()}

                    params.update({'street': classes.get('street')('', '', int(module[1]), '', '', '', '', '', ''), 'cities': classes.get('city').getCities(), 'maps': classes.get('map').getMaps(), 'tileserver': tileserver})
                    return render_template('admin.streets_edit.html', **params)

                elif request.form.get('action').startswith('deletestreets_'):  # delete street
                    db.session.delete(classes.get('street').getStreet(int(request.form.get('action').split('_')[-1])))
                    db.session.commit()
                    cache.clear()

                elif request.form.get('action') == 'savestreet':  # save street
                    if request.form.get('street_id') != 'None':  # update existing street
                        street = classes.get('street').getStreet(int(request.form.get('street_id')))
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
                        cache.delete_memoized(classes.get('city').getStreets)

                    else:  # add street
                        c = request.form.get('edit_cityid').split('_')
                        if len(c) < 2:
                            c.append('')  # subcity
                        city = [ct for ct in classes.get('city').getCities() if str(ct.id) == c[0]][0]
                        city.addStreet(Street(request.form.get('edit_name'), request.form.get('edit_navigation'), int(c[0]), c[1], request.form.get('edit_lat'), request.form.get('edit_lng'), request.form.get('edit_zoom'), request.form.get('edit_active'), ''))
                        db.session.commit()
                    cache.clear()

            try:
                streets = classes.get('city').get_byid(module[-1]).getStreets()
            except AttributeError:
                streets = []
            chars = {}
            for s in streets:
                chars[s.name[0].upper()] = 0
            params.update({'streets': streets, 'chars': sorted(chars.keys()), 'city': classes.get('city').get_byid(int(module[-1]))})
            return render_template('admin.streets.html', **params)

    return "streets"


def getAdminData(self):
    if request.args.get('action') == 'loadcitiesfromosm':  # get city list from osm
        return loadCitiesFromOsm()

    elif request.args.get('action') == 'createcity':  # create cities from osm
        osmids = [c.osmid for c in City.getCities()]
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
        return loadStreetsFromOsm(classes.get('city').get_byid(int(request.args.get('cityid'))))

    elif request.args.get('action') == 'createstreet':  # create streets from osm
        city = classes.get('city').get_byid(int(request.args.get('cityid')))
        ids = [int(i) for i in request.args.get('values').split(",")]  # ids to create
        osmdata = loadStreetsFromOsm(city=city, format='data')

        i = 0
        for sname in osmdata:
            if len(set(osmdata[sname]['osmids']).intersection(set(ids))) > 0:  # add street
                _s = osmdata[sname]
                #db.session.add(Street(sname, '', int(request.args.get('cityid')), '', _s['center'][0], _s['center'][1], 17, 1, _s['osmids'][0]))
                #db.session.commit()
                city.addStreet(
                    Street(sname, '', int(request.args.get('cityid')), '', _s['center'][0], _s['center'][1], 17, 1,
                           _s['osmids'][0]))
                i += 1
        flash(babel.gettext('%(i)s admin.streets.osmstreetsadded', i=i))
        return '1'

    elif request.args.get('action') == 'loadhnumbersfromosm':
        if 'streetid' in request.args:
            streets = [classes.get('street').getStreet(request.args.get('streetid'))]
        elif 'cityid' in request.args:
            streets = [s for s in classes.get('street').getAllStreets() if s.cityid == int(request.args.get('cityid'))]
        else:
            streets = classes.get('street').getAllStreets()

        return str(scheduler.add_single_job(loadHousenumbersFromOsm, [streets]))

    elif request.args.get('action') == 'loadhnumbers':  # load all housenumbers for street
        street = Street.getStreet(int(request.args.get('streetid')))
        ret = dict()
        for hn in street.housenumbers:
            ret[hn.id] = hn.points
        return ret

    elif request.args.get('action') == 'delhousenumber':  # delete housenumber
        hn = classes.get('housenumber').getHousenumbers(int(request.args.get('housenumberid')))
        street = classes.get('street').getStreet(hn.streetid)
        db.session.delete(hn)
        db.session.commit()
        return render_template('admin.streets.housenumber.html', hnumbers=street.housenumbers)

    elif request.args.get('action') == 'addhousenumber':  # add housenumber
        street = classes.get('street').getStreet(int(request.args.get('streetid')))
        points = []
        p = request.args.get('points').split(';')
        points.append((float(p[0]), float(p[1])))
        street.addHouseNumber(request.args.get('hnumber'), points)
        return render_template('admin.streets.housenumber.html', hnumbers=street.housenumbers)

    return "NONE"