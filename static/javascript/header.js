var $header = $('.header');
var $logoText = $('#logoText');
var $logoM = $('#logoM');
var $eventInfo = $('#eventInfo');
var $headerButtons = $('#headerButtons');
var $menuDropdown = $('#headerDropdown');
var $menuTrigger = $('#dropdownTrigger');
var $menuContent = $('#dropdownContent');

$(window).scroll(function() {
    var scrollValue = Math.max($(this).scrollTop(), 0);

    if (scrollValue < 60) {
        $header.css("height", 120 - scrollValue);
        $header.removeClass("header-condensed");
        $eventInfo.css("padding-left", 50 - 25 * scrollValue / 60);
        $headerButtons.css("padding-right", 50 - 25 * scrollValue / 60);
        $menuDropdown.css("padding-right", 50 - 25 * scrollValue / 60);
        $menuContent.css("top", 120 - scrollValue);
        if(scrollValue < 45) {
            $logoText.removeClass("visibilityHidden");
            if(scrollValue > 15) {
                $logoText.css("opacity", (45.0 - scrollValue) / 30.0);
                $logoM.css("height", (74.2 + 15.8 * (1 - (45.0 - scrollValue) / 30.0)) + "%");
            } else {
                $logoText.css("opacity", 1);
                $logoM.css("height", "74.2%");
            }
        } else {
            $logoText.css("opacity", 0);
            $logoText.addClass("visibilityHidden");
            $logoM.css("height", "90%");
        }
    } else {
        $header.css("height", 60);
        $header.addClass("header-condensed");
        $eventInfo.css("padding-left", 25);
        $headerButtons.css("padding-right", 25);
        $menuDropdown.css("padding-right", 25);
        $menuContent.css("top", 60);
        $logoText.css("opacity", 0);
        $logoText.addClass("visibilityHidden");
        $logoM.css("height", "90%");
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