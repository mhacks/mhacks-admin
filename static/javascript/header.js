var $header = $('.header');
var $headerPad = $('#header-pad');
var $headerDropdown = $('#headerDropdown');
var $logoText = $('#logo-text');
var $logoScale = $('.logo-scale');
var $eventInfo = $('#eventInfo');
var $headerButtons = $('#headerButtons');
var $menuDropdown = $('#headerDropdown');
var $menuTrigger = $('#dropdownTrigger');
var $menuContent = $('#dropdownContent');

var shouldScale = window.location.pathname == '/';

$(document).ready(function(){
    var scrollValue = Math.max($(window).scrollTop(), 0);
    var screenHeight = $(window).innerHeight();
    var multiplier = scrollValue / screenHeight;
    if (shouldScale){
        $header.css("height", "100%");
        $header.css("box-shadow", "none");
        $header.css("z-index", 1);
        if (multiplier < 1){
            $logoScale.css("transform", "scale(" + (3 - multiplier * 2) + ")");
            //$eventInfo.css("opacity", 0);
            //$headerButtons.css("opacity", 0);
            //$headerDropdown.css("opacity", 0);
        }
    } else {
        // not on home page
        $header.css("opacity", 0.95);
        $logoScale.css("transform", "scale(1)");
        //$eventInfo.css("opacity", 1);
        //$headerButtons.css("opacity", 1);
        //$headerDropdown.css("opacity", 1);
        $logoText.removeClass('logo-scale');
        $headerPad.css("padding-top", 60);
    }
});

$(window).scroll(function() {
    var scrollValue = Math.max($(window).scrollTop(), 0);
    var screenHeight = $(window).innerHeight();
    var screenWidth = $(window).innerWidth();
    var multiplier = scrollValue / screenHeight;
    if (multiplier < 1 && shouldScale){
        $logoScale.css("transform", "scale(" + (3 - multiplier * 2) + ")");
        $header.css("height", (1.1 - multiplier) * 100 + "vh");
        //$eventInfo.css("opacity", 0);
        //$headerButtons.css("opacity", 0);
        //$headerDropdown.css("opacity", 0);
    } else {
        $header.css("opacity", 0.95);
        $logoScale.css("transform", "scale(1)");
        
        // button visibility
        /*$eventInfo.css("transition", "opacity 1s ease");
        $headerButtons.css("transition", "opacity 1s ease");
        $headerDropdown.css("transition", "opacity 1s ease");*/
        //$eventInfo.css("opacity", 1);
        //$headerButtons.css("opacity", 1);
        //$headerDropdown.css("opacity", 1);

        $logoText.removeClass('logo-scale');
        $headerPad.css("padding-top", 60);
        $header.css("height", 60);
        $header.css("z-index", 99999);
        //$headerButtons.css("padding-right", 25);
        //$menuContent.css("top", 60);
    }
});

$(window).resize(function (){
    if($(window).innerWidth() > 720){
        //$menuContent.slideUp();
        $menuContent.removeClass("expanded");

        $headerButtons.show();//css("opacity", 1);
        $headerDropdown.hide();//css("opacity", 0);
    } else {
        $headerButtons.hide();//css("opacity", 0);
        $headerDropdown.show();//css("opacity", 1);
    }
});

//$menuContent.css("display", "none");
if($(window).innerWidth() > 720){
    $headerButtons.show();//css("opacity", 1);
    $headerDropdown.hide();//css("opacity", 0);
} else {
    $headerButtons.hide();//css("opacity", 0);
    $headerDropdown.show();//css("opacity", 1);
}

$menuTrigger.click(function(){
    //$menuContent.slideToggle();
    //$menuContent.toggle("slide", "right", "500");
    $menuContent.toggleClass("expanded");
});