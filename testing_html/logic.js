// Store our API endpoint as queryUrl
var queryUrl = "http://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2014-01-01&endtime=" +
  "2014-01-02&maxlongitude=-69.52148437&minlongitude=-123.83789062&maxlatitude=48.74894534&minlatitude=25.16517337";

var geomarker=[];
// Perform a GET request to the query URL
d3.json(queryUrl, function(data) {
  console.log(data.features);
  // console.log(data.features.geometry.coordinates.slice(0,3));
  console.log(data.features.geometry);
  array_1=data.features;
  output=array_1.map(data=>data.geometry.coordinates.slice(0,2));
  console.log(output);

  for(var i=0; i<output.length;i++)
      {console.log(output[i]);
        geomarker.push
        (
         L.marker(output[i])
        ) 
      }
  });
  // Using the features array sent back in the API data, create a GeoJSON layer and add it to the map
  // var input=data.features.geometry.coordinates;
  // geomarker.push(
  //   L.circle(input.slice(0,3), {
  //     stroke: false,
  //     fillOpacity: 0.75,
  //     color: "white",
  //     fillColor: "white",
  //     radius: 3})
  //   );
  // });
console.log(geomarker);
var geoLayer = L.layerGroup(geomarker);
// Define streetmap and darkmap layers
var streetmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/outdoors-v10/tiles/256/{z}/{x}/{y}?" +
  "access_token=pk.eyJ1IjoieWl6aGl5aW4iLCJhIjoiY2plbTJwc2s0NGJnOTJ4bzc5M2Uyb3dmcSJ9.s5k3QArmTecuSneRayd8fg");

var darkmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/dark-v9/tiles/256/{z}/{x}/{y}?" +
  "access_token=pk.eyJ1IjoieWl6aGl5aW4iLCJhIjoiY2plbTJwc2s0NGJnOTJ4bzc5M2Uyb3dmcSJ9.s5k3QArmTecuSneRayd8fg");

// Define a baseMaps object to hold our base layers
var baseMaps = {
  "Street Map": streetmap,
  "Dark Map": darkmap
};

var overlayMaps = {
  "Earth Quake":geoLayer
};

// Create a new map
var myMap = L.map("map", {
  center: [
    37.09, -95.71
  ],
  zoom: 5,
  layers: [streetmap]
});

// Create a layer control containing our baseMaps
// Be sure to add an overlay Layer containing the earthquake GeoJSON
L.control.layers(baseMaps,overlayMaps).addTo(myMap);
