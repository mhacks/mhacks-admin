var $packery = $('.grid').packery({
    itemSelector: '.grid-item',
    columnWidth: 160,
    isFitWidth: true,
    stamp: '.stamp'
});
var resizeEvent;
var openElement = null;

var $header = $('.header');
var $logoText = $('#logoText');
var $logoM = $('#logoM');
var $eventInfo = $('#eventInfo');
var $headerButtons = $('#headerButtons');
var $menuDropdown = $('#headerDropdown');
var $menuTrigger = $('#dropdownTrigger');
var $menuContent = $('#dropdownContent');

$packery.on('click', '.grid-item, .grid-item-expand', function(event){
    var item = $(event.currentTarget);

    if(event.target.tagName.toUpperCase() == "A"){
        return;
    }

    if(item.data("expandable") != 1){
        return;
    }

    if(openElement !== null && openElement !== event.currentTarget){
        var openItem = $(openElement);

        openItem.toggleClass('grid-item-expand');
        openItem.toggleClass('grid-item');
        openItem.toggleClass('stamp');
    }

    var isExpanded = item.hasClass('grid-item-expand');
    item.toggleClass('grid-item-expand');
    item.toggleClass('grid-item');
    item.toggleClass('stamp');

    if(isExpanded){
        // was expanded, now shrinking
        setTimeout(function(){$packery.packery('shiftLayout');}, 250);
    } else {
        // is expanding
        setTimeout(function(){$packery.packery('fit', event.currentTarget);}, 250);
    }

    openElement = isExpanded ? null : event.currentTarget;
});

$(window).resize(function () {
    clearTimeout(resizeEvent);
    resizeEvent = setTimeout(function () {
        $packery.packery();
    }, 250);

    if($(window).innerWidth() > 720){
        $menuContent.slideUp();
    }
});

$(window).scroll(function() {
    var scrollValue = $(this).scrollTop();

    if(scrollValue < 60){
        $header.css("height", 120 - scrollValue);
        $header.removeClass("header-condensed");
        $eventInfo.css("padding-left", 50 - 25 * scrollValue / 60);
        $headerButtons.css("padding-right", 50 - 25 * scrollValue / 60);
        $menuDropdown.css("padding-right", 50 - 25 * scrollValue / 60);
        $menuContent.css("top", 120 - scrollValue);
        if(scrollValue < 45){
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
        $header.addClass("header-condensed");
        $logoText.css("opacity", 0);
        $logoText.addClass("visibilityHidden");
        $logoM.css("height", "90%");
    }
});

$menuContent.css("display", "none");

$menuTrigger.click(function(){
    $menuContent.slideToggle();
});