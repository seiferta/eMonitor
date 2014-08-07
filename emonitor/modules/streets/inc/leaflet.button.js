L.Control.ZoomHome = L.Control.Zoom.extend({
    options: {
      position: "topleft",
      zoomInText: "+",
      zoomInTitle: "Zoom in",
      zoomOutText: "-",
      zoomOutTitle: "Zoom out",
      zoomHomeText: "Zoom Home",
      zoomHomeTitle: "Zoom Home"
    },

    onAdd: function (map) {
        this._map = map;

        var zoomName = "leaflet-control-zoom"
          , container = L.DomUtil.create("div", zoomName + " leaflet-bar")
          , options = this.options;

        this._zoomInButton = this._createButton(options.zoomInText, options.zoomInTitle,
          zoomName + '-in', container, this._zoomIn, this);

        this._zoomOutButton = this._createButton(options.zoomOutText, options.zoomOutTitle,
          zoomName + '-out', container, this._zoomOut, this);

        this._zoomHomeButton = this._createButton(options.zoomHomeText, options.zoomHomeTitle,
          zoomName + '-home', container, this._zoomHome, this);

        this._updateDisabled();
        map.on('zoomend zoomlevelschange', this._updateDisabled, this);
        return container
    },

    _zoomHome: function () {
        this._map.setView(new L.LatLng(startlat, startlng), startzoom);
    }
});
