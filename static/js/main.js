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

