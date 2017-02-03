var $header = $('.header');
var $headerPad = $('#header-pad');
var $logoText = $('#logo-text');
var $logoScale = $('.logo-scale');
var $eventInfo = $('#eventInfo');
var $headerButtons = $('#headerButtons');
var $menuDropdown = $('#headerDropdown');
var $menuTrigger = $('#dropdownTrigger');
var $menuContent = $('#dropdownContent');

var shouldScale = window.location.pathname == '/';
$(document).ready(function(){
    if (shouldScale){
        $header.css("height", "100%");
    } else {
        // not on home page
        $header.css("opacity", 0.95);
        $logoScale.css("transform", "scale(1)");
        $eventInfo.css("opacity", 1);
        $headerButtons.css("opacity", 1);
        $logoText.removeClass('logo-scale');
        $headerPad.css("padding-top", 60);
    }
});

$(window).scroll(function() {
    var scrollValue = Math.max($(this).scrollTop(), 0);
    
    // additional animations done on the home page
    if (shouldScale){    
        if (scrollValue > 70) {
            $logoScale.css("transform", "scale(1)");
            $logoText.removeClass('logo-scale');
            $header.css("opacity", 0.95);

        } else {
            $logoScale.css("transform", "scale(" + (100-scrollValue)/ 30 + ")");
            $header.css("opacity", 1);
            if (scrollValue < 60) $header.css("height", 100 - scrollValue + "vh");
            if(scrollValue < 45) {    
                if(scrollValue > 15) {
                    $eventInfo.css("opacity", (scrollValue - 15.0) / 30.0);
                    $headerButtons.css("opacity", (scrollValue - 15.0) / 30.0);
                } else {
                    $eventInfo.css("opacity", 0);
                    $headerButtons.css("opacity", 0); 
                }
            } else {
                $eventInfo.css("opacity", 1);
                $headerButtons.css("opacity", 1);
                $logoScale.css("transform", "scale(1)");
                shouldScale = false;

            }
        }
    }
    
    // animations that are used on every page
    if (scrollValue < 60) {
        $header.removeClass("header-condensed");
        $eventInfo.css("padding-left", 50 - 25 * scrollValue / 60);
        $headerButtons.css("padding-right", 50 - 25 * scrollValue / 60);
        $menuDropdown.css("padding-right", 50 - 25 * scrollValue / 60);
        $menuContent.css("top", 120 - scrollValue);  
    } else {
        $header.css("height", 60);
        $header.addClass("header-condensed");
        $eventInfo.css("padding-left", 25);
        $headerButtons.css("padding-right", 25);
        $menuDropdown.css("padding-right", 25);
        $menuContent.css("top", 60);
        $eventInfo.css("opacity", 1);
        $headerButtons.css("opacity", 1);
    }
});

$(window).resize(function (){
    if($(window).innerWidth() > 720){
        $menuContent.slideUp();
    }
});

$menuContent.css("display", "none");

$menuTrigger.click(function(){
    $menuContent.slideToggle();
});