function init() {
	var elem = document.getElementById('favInput');
	var autocomplete = new google.maps.places.Autocomplete(elem);
}

google.maps.event.addDomListener(window, 'load', init);