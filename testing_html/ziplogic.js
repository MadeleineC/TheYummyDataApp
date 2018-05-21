
// Define streetmap and darkmap layers
var streetmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/outdoors-v10/tiles/256/{z}/{x}/{y}?" +
  "access_token=pk.eyJ1IjoieWl6aGl5aW4iLCJhIjoiY2plbTJwc2s0NGJnOTJ4bzc5M2Uyb3dmcSJ9.s5k3QArmTecuSneRayd8fg");

var darkmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/dark-v9/tiles/256/{z}/{x}/{y}?" +
  "access_token=pk.eyJ1IjoieWl6aGl5aW4iLCJhIjoiY2plbTJwc2s0NGJnOTJ4bzc5M2Uyb3dmcSJ9.s5k3QArmTecuSneRayd8fg");
  
var ziptile = L.tileLayer('https://api.mapbox.com/styles/v1/yizhiyin/cjhdj4umj1pir2sqmpgo2sl68/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoieWl6aGl5aW4iLCJhIjoiY2plbTJwc2s0NGJnOTJ4bzc5M2Uyb3dmcSJ9.s5k3QArmTecuSneRayd8fg')
// Define a baseMaps object to hold our base layers
var baseMaps = {
  "Street Map": streetmap,
  "Dark Map": darkmap
};

var overlayMaps = {
  "Zip":ziptile
};

// Create a new map
var myMap = L.map("map", {
  center: [
    30.307182, -97.755996
  ],
  zoom: 8,
  layers: [ziptile]
});

// Create a layer control containing our baseMaps
// Be sure to add an overlay Layer containing the earthquake GeoJSON
L.control.layers(baseMaps,overlayMaps).addTo(myMap);
