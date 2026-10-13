'use strict';
const map=L.map('map',{preferCanvas:true,zoomControl:true,attributionControl:true,zoomAnimation:false,fadeAnimation:false,markerZoomAnimation:false}).setView([-22,-47],12);
L.control.scale({imperial:false,position:'bottomleft'}).addTo(map);
const shapes=new Map();let bridge=null;let selected=null;let raster=null;let online=false;
function style(feature){return {color:feature.properties.preview?'#eac65b':'#39b980',weight:2,fillOpacity:0.2};}
window.agro={
 ready:false,
 viewState(){return {zoom:map.getZoom(),center:map.getCenter(),count:shapes.size,selected};},
 collection(data,fit){
  for(const layer of shapes.values()) map.removeLayer(layer);shapes.clear();selected=null;
  const bounds=L.latLngBounds([]);
  for(const feature of data.features){
   const layer=L.geoJSON(feature,{style}).addTo(map);shapes.set(String(feature.id),layer);bounds.extend(layer.getBounds());
   layer.on('click',()=>window.agro.select(String(feature.id)));
  }
  document.getElementById('empty').hidden=shapes.size>0;
  if(fit&&bounds.isValid())map.fitBounds(bounds,{padding:[30,30],maxZoom:19,animate:false});
  map.invalidateSize();
 },
 select(id){
  if(!shapes.has(id))return;
  if(selected&&shapes.has(selected))shapes.get(selected).setStyle({weight:2});
  selected=id;shapes.get(id).setStyle({weight:4});
  if(bridge)bridge.selected(id);
 },
 fit(id){if(id&&shapes.has(id))map.fitBounds(shapes.get(id).getBounds(),{padding:[30,30],maxZoom:19,animate:false});
  else {const b=L.latLngBounds([]);for(const layer of shapes.values())b.extend(layer.getBounds());if(b.isValid())map.fitBounds(b,{padding:[30,30],maxZoom:19,animate:false});}},
 zoom(amount){map.setZoom(map.getZoom()+amount);},
 layers(items){for(const item of items){const layer=shapes.get(item.id);if(!layer)continue;
  if(item.visible){if(!map.hasLayer(layer))layer.addTo(map);layer.setStyle({color:item.color,opacity:item.opacity,fillOpacity:item.opacity*0.2});layer.bringToFront();}
  else if(map.hasLayer(layer))map.removeLayer(layer);}},
 imagery(config){if(raster)map.removeLayer(raster);raster=null;
  if(config){raster=L.tileLayer(config.url,{attribution:config.attribution,minZoom:0,maxZoom:19,crossOrigin:false});if(online)raster.addTo(map);}},
 online(value){online=value;if(raster){if(value)raster.addTo(map);else map.removeLayer(raster);}}
};
map.on('mousemove',e=>{document.getElementById('coordinates').textContent=`${e.latlng.lat.toFixed(7)}, ${e.latlng.lng.toFixed(7)} · WGS84 | visualização EPSG:3857`;});
new QWebChannel(qt.webChannelTransport,channel=>{bridge=channel.objects.bridge;window.agro.ready=true;bridge.ready();});
