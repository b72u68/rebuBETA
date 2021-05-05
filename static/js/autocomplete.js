/*******************
**** FAV PLACES ****
********************/
function favPick(e){
    document.getElementById('ridePickup').value = e.target.value;
    document.getElementById("favPlcP").selectedIndex = 0;
}
function favDest(e){
    document.getElementById('rideDestination').value = e.target.value;
    document.getElementById('favPlcD').selectedIndex = 0;
}
/*******************
 **** ADD STOPS  ****
 ********************/
var i = "stop";
var stopMrk = "http://maps.google.com/mapfiles/ms/icons/blue-dot.png";

function addStop() {
  i += "1";
  elem = document.createElement("input");
  elem.type = "text";
  elem.class = "formInput";
  elem.placeholder = "addStop";
  elem.id = i;
  elem.name = i;
  document.getElementById("addStopCtn").appendChild(elem);

  addAutoPop(i, stopMrk);
}

function addAutoPop(id, mrkURL) {
  var elem = document.getElementById(id);
  var autocomplete = new google.maps.places.Autocomplete(elem);

  const marker = new google.maps.Marker({
    map,
    icon: mrkURL,
  });

  autocomplete.addListener("place_changed", () => {
    marker.setVisible(false);
    const place = autocomplete.getPlace();
    marker.setPosition(place.geometry.location);
    marker.setVisible(true);
    map.setCenter(place.geometry.location);
    map.setZoom(14);
  });
}

function init() {
    addAutoPop('ridePickup', 'http://maps.google.com/mapfiles/ms/icons/red-dot.png')
    addAutoPop('rideDestination', 'http://maps.google.com/mapfiles/ms/icons/green-dot.png')
    // disable enter from adding stop
    window.addEventListener('keydown',function(e){if(e.keyIdentifier=='U+000A'||e.keyIdentifier=='Enter'||e.keyCode==13){if(e.target.nodeName=='INPUT'&&e.target.type=='text'){e.preventDefault();return false;}}},true);
}
google.maps.event.addDomListener(window, "load", init);

