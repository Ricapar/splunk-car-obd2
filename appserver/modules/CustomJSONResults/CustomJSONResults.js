// A simple results table
Splunk.Module.CustomJSONResults = $.klass(Splunk.Module.DispatchingModule, {

    /*
     * overriding initialize to set up references and event handlers.
     */
    initialize: function($super, container) {
        $super(container);
        this.myParam = this.getParam("myParam");
        this.resultsContainer = this.container;

        if(typeof google == "undefined") {
            return;
        }

        var nj = new google.maps.LatLng(40.81597, -74.295364);
        var mapOptions = {
            mapTypeControlOptions: {  
                mapTypeIds: ['Trip Map']  
            },  
            zoom: 11,
            center: nj,
            mapTypeId: 'Trip Map'
        }

        var styles = [
  {
    "stylers": [
      { "invert_lightness": true },
      { "weight": 0.8 }
    ]
  },{
    "featureType": "poi",
    "elementType": "geometry",
    "stylers": [
      { "visibility": "off" }
    ]
  },{
    "featureType": "road",
    "elementType": "geometry",
    "stylers": [
      { "weight": 0.5 },
      { "hue": "#ff6e00" }
    ]
  }
];

        this.map = new google.maps.Map(document.getElementById('GoogleMapDiv'), mapOptions);
        var styledMapType = new google.maps.StyledMapType(styles, { name: 'Trip Map' });  
        this.map.mapTypes.set('Trip Map', styledMapType); 



        // var ctaLayer = new google.maps.KmlLayer({
        //     url: 'http://gmaps-samples.googlecode.com/svn/trunk/ggeoxml/cta.kml'
        // });
        // ctaLayer.setMap(map);

        // google.maps.event.addDomListener(window, 'load', initialize);


    },

    onJobDone: function(event) {
        console.log("onJobDone called");
        this.getResults();
    },

    getResultParams: function($super) {
        console.log("getResultParms called");
        var params = $super();
        var context = this.getContext();
        var search = context.get("search");
        var sid = search.job.getSearchId();

        if (!sid) this.logger.error(this.moduleType, "Assertion Failed.");

        params.sid = sid;
        return params;
    },

     renderResults: function($super, htmlFragment) {
        console.log("renderResults called");
        if (!htmlFragment) {
            this.resultsContainer.html('No content available.');
            return;
        }
        eval(htmlFragment);
    }

})
