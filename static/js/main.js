function toggleMenu() {
  var x = document.getElementById("hiddenMenu");
  if (x.style.display === "none") {
    x.style.display = "block";
  } else {
    x.style.display = "none";
  }
}

function toggleStatus() {
  var x = document.getElementById("statusSubcontainerOn");
  var y = document.getElementById("statusSubcontainerOff");
  rideRequestContainer = document.getElementById("rideRequestContainer");
  rideInfoContainer = document.getElementById("rideInfoContainer");

  if (x.style.display === "block") {
    x.style.display = "none";
    y.style.display = "block";
    rideInfoContainer.style.display = "none";
    rideRequestContainer.style.display = "block";
    toggleRides();
  } else {
    x.style.display = "block";
    y.style.display = "none";
    rideInfoContainer.style.display = "none";
    rideRequestContainer.style.display = "block";
    toggleRides();
  }
}

function toggleRides() {
  var x = document.getElementById("onlineRideContainer");
  var y = document.getElementById("offlineRidesContainer");

  if (x.style.display === "block") {
    y.style.display = "block";
    x.style.display = "none";
  } else {
    y.style.display = "none";
    x.style.display = "block";
  }
}

function refreshRideRequests() {
  navigator.geolocation.getCurrentPosition(function (position) {
    let lat = position.coords.latitude;
    let lng = position.coords.longitude;

    $.post("/api/get_nearby_rides?lat=" + lat + "&lng=" + lng, function (data) {
      console.log(data);
      document.getElementById("rideRequestList").innerHTML = data;
    });
  });
}

function viewRideInfo(id) {
  rideRequestContainer = document.getElementById("rideRequestContainer");
  rideInfoContainer = document.getElementById("rideInfoContainer");

  navigator.geolocation.getCurrentPosition(function (position) {
    let lat = position.coords.latitude;
    let lng = position.coords.longitude;

    $.post(
      "/api/get_ride_info?id=" + id + "&lat=" + lat + "&lng=" + lng,
      function (data) {
        console.log(data);
        rideRequestContainer.style.display = "none";
        rideInfoContainer.style.display = "block";
        document.getElementById("rideInformation").innerHTML = data;
      }
    );
  });
}

function acceptRide(id) {
  navigator.geolocation.getCurrentPosition(function (position) {
    let lat = position.coords.latitude;
    let lng = position.coords.longitude;

    $.post(
      "/ride/accept?id=" + id + "&lat=" + lat + "&lng=" + lng,
      function (data) {
        window.location.href = data;
      }
    );
  });
}

function closeRideInfo() {
  rideRequestContainer = document.getElementById("rideRequestContainer");
  rideInfoContainer = document.getElementById("rideInfoContainer");

  rideRequestContainer.style.display = "block";
  rideInfoContainer.style.display = "none";
}

function cancelRide(id) {
  $.post("/ride/cancel?id=" + id, function (data) {
    window.location.href = data;
  });
}

function confirmPickup(id) {
  $.post("/ride/pickup/confirm?id=" + id, function (data) {
    window.location.href = data;
  });
}

function confirmDropoff(id) {
  $.post("/ride/dropoff/confirm?id=" + id, function (data) {
    window.location.href = data;
  });
}

function onChoosingFavoritePickup(location) {
  document.getElementById("ridePickup").value = location;
}

function onChoosingFavoriteDest(location) {
  document.getElementById("rideDestination").value = location;
}
