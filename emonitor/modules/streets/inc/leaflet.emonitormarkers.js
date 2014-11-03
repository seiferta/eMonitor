
L.EmonitorMarkers = L.Class.extend({
    options: {
        debug: false,
        shadowicon: '/img/marker-shadow.png',
        redmarkericon: '/img/marker_red.png',
        orangemarkericon: '/img/marker_orange.png',
        yellowmarkericon: '/img/marker_yellow.png',
        greymarkericon:'/img/marker_sw.png'
    },

    initialize: function (options) {
        if(this.debug == true) console.log('init housenumbers');
        L.Util.setOptions(this, options);
        var MyMarker = L.Icon.extend({options: {shadowUrl:this.options.shadowicon, iconAnchor: [12, 41], popupAnchor: [0, -42]}});
        var redmarker = new MyMarker({iconUrl:this.options.redmarkericon});
        var orangemarker = new MyMarker({iconUrl:this.options.orangemarkericon});
        var yellowmarker = new MyMarker({iconUrl:this.options.yellowmarkericon});
        var greymarker = new MyMarker({iconUrl:this.options.greymarkericon});

        this.options = {'colorcode': [yellowmarker, orangemarker, redmarker],
            'redmarker': redmarker};

        this._housenumbers = new L.LayerGroup();
        this._alarmmarkers = new L.LayerGroup();
        this._alarmroute = new L.LayerGroup();
    },

    addTo: function (map) {
        if(this.debug == true) console.log('add new layers for marker, housenumber and route');
        this._map = map;
        this._map.emonitormarkersoptions = this.options;

        if (this._map.hasLayer(this._alarmmarkers)){
            this._map.clearLayers(this._alarmmarkers);
        }else{
            var markers_alarm = this._alarmmarkers.addTo(this._map);
        }

        if (this._map.hasLayer(this._housenumbers)){
            this._map.clearLayers(this._housenumbers);
        }else{
            var markers_hn = this._housenumbers.addTo(this._map);
        }

        if (this._map.hasLayer(this._alarmroute)){
            this._map.clearLayers(this._alarmroute);
        }else{
            var markers_route = this._alarmroute.addTo(this._map);
        }

        map.emonitoroptions = this.options;

        /* marker section */
        map.addMarker=function(lat, lng, prio, moveable){
            var m;
            if(lat && lng){
                if (prio){
                    m = new L.Marker(new L.LatLng(lat, lng), {icon:this.emonitoroptions.colorcode[parseInt(prio)],draggable:moveable});
                }else{
                    m = new L.Marker(new L.LatLng(lat, lng), {icon:this.emonitoroptions.redmarker,draggable:moveable});
                }
                markers_alarm.addLayer(m);
            }
            return m;
        };

        map.clearMarkers=function(){
            markers_alarm.clearLayers();
        };

        /* housenumber section */
        map.addHouseNumber=function(coords){
            if (coords.lat){
                 var polygonPoints = [];
                 $.each(coords.lat, function(index) {
                     polygonPoints.push(new L.LatLng(coords.lat[index], coords.lng[index]));
                 });
                 markers_hn.addLayer(new L.Polygon(polygonPoints));
                 this.setView(new L.LatLng(coords.lat[0], coords.lng[0]), this.getZoom());
             }
        };

        map.clearHouseNumbers=function(){
            //if(this.emonitormarkeroptions.debug == true) console.log('clearNumbers');
            markers_hn.clearLayers();
        };

        map.clearRoute=function(){
            markers_route.clearLayers();
        };

        map.addRoute=function(data){
            var linePoints = [];
            $.each(data.coordinates, function(index){
                linePoints.push(new L.LatLng(data.coordinates[index][1], data.coordinates[index][0]));
            });
            markers_route.addLayer(new L.Polyline(linePoints, {color: 'blue', weight: map.getZoom()/2, opacity:0.5, smoothFactor:1}));
        };

        return this;
    },

    onRemove: function(map){
         //this._map.clearLayers(this._housenumbers);
    }

});

