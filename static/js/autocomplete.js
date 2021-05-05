/*******************
 **** FAV PLACES ****
 ********************/
function ersPck() {
  document.getElementById("ridePickup").value = "";
}
function ersFavP() {
  document.getElementById("favPlcP").selectedIndex = 0;
}
function ersDst() {
  document.getElementById("rideDestination").value = "";
}
function ersFavD() {
  document.getElementById("favPlcD").selectedIndex = 0;
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
  addAutoPop(
    "ridePickup",
    "http://maps.google.com/mapfiles/ms/icons/red-dot.png"
  );
  addAutoPop(
    "rideDestination",
    "http://maps.google.com/mapfiles/ms/icons/green-dot.png"
  );
}
google.maps.event.addDomListener(window, "load", init);

