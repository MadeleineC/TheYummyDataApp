var zipcodetosearch=['78702','78759','78732','78736'];
var population=[1000,2000,3000,4000];
var selectedgeo=[];
var plotgeo={};
d3.json('zips.json',function(zipdata){
    var features=zipdata.features;
    for (var i=0;i<zipcodetosearch.length;i++){
        for (var j=0;j<features.length;j++){
            var featureobj=features[j];
            if(featureobj.properties.ZCTA5CE10==zipcodetosearch[i]){
            featureobj.properties['population']=population[i];
            selectedgeo.push(featureobj);
            console.log(selectedgeo);

            }  
        }
    }

plotgeo['type']='"FeatureCollection"';
plotgeo['name']="cb_2017_us_zcta510_500k";
plotgeo['features']=selectedgeo;

console.log(plotgeo);
createFeatures(plotgeo);

});


function createFeatures(plotgeo) {
    var streetmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/outdoors-v10/tiles/256/{z}/{x}/{y}?" +
      "access_token=pk.eyJ1IjoieWl6aGl5aW4iLCJhIjoiY2plbTJwc2s0NGJnOTJ4bzc5M2Uyb3dmcSJ9.s5k3QArmTecuSneRayd8fg");
    
    var satellite = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v9/tiles/256/{z}/{x}/{y}?" +
      "access_token=pk.eyJ1IjoieWl6aGl5aW4iLCJhIjoiY2plbTJwc2s0NGJnOTJ4bzc5M2Uyb3dmcSJ9.s5k3QArmTecuSneRayd8fg");
    
      function getColor(d) {
        return d > 3000 ? '#800026' :
               d > 2000 ? '#BD0026' :
               d > 1000  ? '#E31A1C' :
                          '#FFEDA0';
    }

    function style(feature) {
        return {
            fillColor: getColor(feature.properties.population),
            weight: 2,
            opacity: 1,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.7
        };
    }

    
    function highlightFeature(e) {
            var layer = e.target;
            
            layer.setStyle({
                 weight: 4,
                color: '#31a354',
                dashArray: '',
                fillOpacity: 0.7
                });
            
            if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                    layer.bringToFront();
                }
            }
    function resetHighlight(e) {
            geojson.resetStyle(e.target);
            }
   
    function onEachFeature(feature, layer) {
            layer.on({
                mouseover: highlightFeature,
                mouseout: resetHighlight
            }).bindPopup("<h3>" + feature.properties.population +" "+ feature.properties.ZCTA5CE10+
             "</h3><hr>");
              }

    var ziptile=L.geoJSON(plotgeo,{style:style,onEachFeature: onEachFeature});

    var baseMaps = {
        "Street Map": streetmap,
        "Satellite Map": satellite
      };
    
      var overlayMaps = {
        Zipcode: ziptile
      };
    var myMap = L.map("map", {
        center: [30.307182, -97.755996],
        zoom: 10,
        layers: [streetmap, ziptile]
      });
    L.control.layers(baseMaps, overlayMaps, {
          collapsed: false
        }).addTo(myMap);
    var legend = L.control({position: 'bottomright'});
    legend.onAdd = function (map) {
    
        var div = L.DomUtil.create('div', 'info legend'),
                grades = [0, 1000, 2000, 3000],
                labels = [];
        
            // loop through our density intervals and generate a label with a colored square for each interval
        for (var i = 0; i < grades.length; i++) {
                div.innerHTML +=
                    '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +
                    grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
            }
        
            return div;
        };
        legend.addTo(myMap);
    
    }
    

    


//     // Define a function we want to run once for each feature in the features array
//     // Give each feature a popup describing the place and time of the earthquake
//     function onEachFeature(feature, layer) {
//       layer.bindPopup("<h3>" + feature.properties.population +" "+ feature.properties.ZCTA5CE10+
//         "</h3><hr>");
//     }


//     // Create a GeoJSON layer containing the features array on the earthquakeData object
//     // function colorscale(pop){
//     //     return pop >3000 ? '#bd0026' :
//     //            pop >2000 ? '#f03b20':
//     //            pop >1000  ? '#fd8d3c':
//     //            '#feb24c' ;         
//     //   }

    
//     function style(feature) {
//         return {
//         fillcolor: function(feature){
//             return feature.properties.population >3000 ? 'red' :
//             feature.properties.population >2000 ? 'blue':
//             feature.properties.population >1000  ? 'yellow':
//             '#feb24c'
//         },
//         weight: 2,
//         opacity: 1,
//         color: 'red',
//         dashArray: '3',
//         fillOpacity: 0.7};
//     };
  
//     var zipmap = L.geoJSON(plotgeo, {
//         style: style,
//       // set up the radius of circle Marker cooresponde to the magnitude of the earthquake
//       onEachFeature: onEachFeature
//     });
    
//     createMap(zipmap)
// };

// function createMap(zipmap) {

//     // Define streetmap and darkmap layers
//     var streetmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/outdoors-v10/tiles/256/{z}/{x}/{y}?" +
//       "access_token=pk.eyJ1IjoieWl6aGl5aW4iLCJhIjoiY2plbTJwc2s0NGJnOTJ4bzc5M2Uyb3dmcSJ9.s5k3QArmTecuSneRayd8fg");
  
//     var satellite = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v9/tiles/256/{z}/{x}/{y}?" +
//       "access_token=pk.eyJ1IjoieWl6aGl5aW4iLCJhIjoiY2plbTJwc2s0NGJnOTJ4bzc5M2Uyb3dmcSJ9.s5k3QArmTecuSneRayd8fg");
  
//     // Define a baseMaps object to hold our base layers
//     var baseMaps = {
//       "Street Map": streetmap,
//       "Satellite Map": satellite
//     };
  
//     // Create overlay object to hold our overlay layer
//     var overlayMaps = {
//       Zipcode: zipmap
//     };
  
//     // Create our map, giving it the streetmap and earthquakes layers to display on load
//     var myMap = L.map("map", {
//       center: [
//         30.307182, -97.755996
//       ],
//       zoom: 10,
//       layers: [streetmap, zipmap]
//     });
//     L.control.layers(baseMaps, overlayMaps, {
//         collapsed: false
//       }).addTo(myMap);
// }




