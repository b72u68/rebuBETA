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

  if (x.style.display === "block") {
    x.style.display = "none";
    y.style.display = "block";
    toggleRides();
  } else {
    x.style.display = "block";
    y.style.display = "none";
    toggleRides();
  }
}

function toggleRides() {
  var x = document.getElementsByClassName("rideRow");
  var y = document.getElementById("offlineRidesContainer");

  if (x[0].style.display === "block") {
    y.style.display = "block";
    for (i = 0; i < x.length; i++) {
      x[i].style.display = "none";
    }
  } else {
    y.style.display = "none";
    for (i = 0; i < x.length; i++) {
      x[i].style.display = "block";
    }
  }
}

function getPickup(input) {
  $.get(
    "/api/search_location?loc=" + input.replace(/\s+/g, "+"),
    function (data) {
      document.getElementById("destination_result").innerHTML = "";
      document.getElementById("pickup_result").innerHTML =
        data.name + "<br>" + data.address;
      document.getElementById("pickup").data = data;
    }
  );
}

function getDestination(input) {
  $.get(
    "/api/search_location?loc=" + input.replace(/\s+/g, "+"),
    function (data) {
      document.getElementById("pickup_result").innerHTML = "";
      document.getElementById("destination_result").innerHTML =
        data.name + "<br>" + data.address;
      document.getElementById("destination").data = data;
    }
  );
}

function setPickupLocation(input) {
  let data = document.getElementById("pickup").data;
  document.getElementById("pickup_result").innerHTML = "";
  document.getElementById("pickup").value = data.address;
}

function setDestinationLocation(input) {
  let data = document.getElementById("destination").data;
  document.getElementById("destination_result").innerHTML = "";
  document.getElementById("destination").value = data.address;
}
