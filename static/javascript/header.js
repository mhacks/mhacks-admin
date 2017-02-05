var $header = $('.header');
//var $headerPad = $('#header-pad');
var $headerDropdown = $('#headerDropdown');
var $logoContainer = $('#logo');
var $logo = $('#logo-text');
var $headerButtons = $('#headerButtons');
var $menuTrigger = $('#dropdownTrigger');
var $menuContent = $('#dropdownContent');
var $downScroll = $('#scroll-down');

var shouldScale = window.location.pathname == '/';
var headerScroll = 160;

$(document).ready(function(){
    if (shouldScale){
        var scrollValue = Math.max($(window).scrollTop(), 0);
        if(scrollValue == 0){
            $downScroll.show();
        } else {
            $downScroll.hide();
        }

        if (scrollValue < headerScroll){
            $header.css("opacity", 0.95 + 0.05 * (1 - scrollValue / headerScroll));
            $header.css("height", "calc(" + (1 - scrollValue / headerScroll) + "* (100vh - 100px) + 100px)");
            $logoContainer.css("width", (1 - scrollValue / headerScroll) * 50 + 50 + "vw");
            $logo.css("max-height", "calc((100% - 51px) * " + (scrollValue / headerScroll) + " + 51px)");
        } else {
            $header.css("opacity", 0.95);
            //$headerPad.css("padding-top", 60);
            $header.css("height", 100);
            $logoContainer.css("width", "50vw");
            $logo.css("max-height", "51px");
            $header.css("z-index", 99999);
        }
        $header.css("z-index", 1);
    } else {
        // not on home page
        $header.css("opacity", 0.95);
        //$headerPad.css("padding-top", 60);
        $downScroll.hide();
    }
});

$(window).scroll(function() {
    var scrollValue = Math.max($(window).scrollTop(), 0);

    if (scrollValue < headerScroll && shouldScale){
        $header.css("opacity", 0.95 + 0.05 * (1 - scrollValue / headerScroll));
        $header.css("height", "calc(" + (1 - scrollValue / headerScroll) + "* (100vh - 100px) + 100px)");
        $logoContainer.css("width", (1 - scrollValue / headerScroll) * 50 + 50 + "vw");
        $logo.css("max-height", "calc((100% - 51px) * " + (scrollValue / headerScroll) + " + 51px)");
        if(scrollValue == 0){
            $downScroll.show();
        } else {
            $downScroll.hide();
        }
    } else {
        $header.css("opacity", 0.95);
        //$headerPad.css("padding-top", 60);
        $header.css("height", 100);
        $logoContainer.css("width", "50vw");
        $logo.css("max-height", "51px");
        $header.css("z-index", 99999);
        $downScroll.hide();
    }
});

$(window).resize(function (){
    if($(window).innerWidth() > 720){
        $menuContent.removeClass("expanded");

        $headerButtons.show();
        $headerDropdown.hide();
    } else {
        $headerButtons.hide();
        $headerDropdown.show();
    }
});

if($(window).innerWidth() > 720){
    $headerButtons.show();
    $headerDropdown.hide();
} else {
    $headerButtons.hide();
    $headerDropdown.show();
}

$menuTrigger.click(function(){
    $menuContent.toggleClass("expanded");
});

$downScroll.click(function(event){
    $('html, body').animate({
        scrollTop: headerScroll
    }, 'slow');
});