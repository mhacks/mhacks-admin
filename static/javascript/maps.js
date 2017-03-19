$(document).ready(function(){
    $(".maps-floor").hide();
    $(".maps-floor[data-level='B']").show();
});

$(".maps-link").click(function(event) {
    var chosen = $(event.target);
    if (chosen.data("level") != $(".maps-link.selected").data("level")) {
        selectFloor(chosen.data("level"));
    }
});

function selectFloor(l){
    var selected = $(".maps-link.selected");
    $(".maps-floor[data-level='" + selected.data("level") + "']").stop().slideUp();
    $(".maps-floor[data-level='" + l + "']").stop().slideDown();
    selected.removeClass("selected");
    $(".maps-link[data-level='" + l + "']").addClass("selected");
}

function initMap() {
  var uluru = {lat: -25.363, lng: 131.044};
  var map = new google.maps.Map(document.getElementById('map'), {
    zoom: 4,
    center: uluru
  });
  var marker = new google.maps.Marker({
    position: uluru,
    map: map
  });
}
