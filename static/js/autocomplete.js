// favorite places
function ersDst(){
    document.getElementById('rideDestination').value = '';
}

function ersFav(){
    document.getElementById("favPlaces").selectedIndex = 0;
}


function init() {
    var pickup = document.getElementById('ridePickup');
    var destination = document.getElementById('rideDestination');
    var destination_fav = document.getElementById('favPlaces');

    var autocomplete1 = new google.maps.places.Autocomplete(pickup);
	var autocomplete2 = new google.maps.places.Autocomplete(destination);
    var autocomplete3 = new google.maps.places(destination_fav);

	const startMarker = new google.maps.Marker({
	    map
	});
	const endMarker = new google.maps.Marker({
	    map,
	    icon: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'
	});


	autocomplete1.addListener("place_changed", () => {
		startMarker.setVisible(false);
    	const place = autocomplete1.getPlace();
    	
    	startMarker.setPosition(place.geometry.location);
    	startMarker.setVisible(true);
    	map.setCenter(place.geometry.location);
    	map.setZoom(14);
	});

	autocomplete2.addListener("place_changed", () => {
		endMarker.setVisible(false);
    	const place = autocomplete2.getPlace();
    	
    	endMarker.setPosition(place.geometry.location);
    	endMarker.setVisible(true);
    	map.setCenter(place.geometry.location);
    	map.setZoom(14);
	});


}
google.maps.event.addDomListener(window, 'load', init);