let map;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 41.835, lng: -87.625 },
    zoom: 14,
    streetViewControl: false,
    fullscreenControl: false,
    mapTypeControl: false
  });
}