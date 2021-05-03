let map;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 41.835, lng: -87.625 },
    zoom: 14,
    streetViewControl: false,
    fullscreenControl: false,
    mapTypeControl: false,
  });
}

function init() {
  var pickup = document.getElementById("ridePickup");
  var destination = document.getElementById("rideDestination");
  var autocomplete1 = new google.maps.places.Autocomplete(pickup);
  var autocomplete2 = new google.maps.places.Autocomplete(destination);
}

