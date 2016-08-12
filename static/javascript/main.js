var $bg = document.querySelector('#bgCanvas');
var $bgElem = $('#bgCanvas');
var $grid = $('.grid');
var $header = $('.header');
var $logoText = $('#logoText');
var $logoM = $('#logoM');
var $eventInfo = $('#eventInfo');
var $headerButtons = $('#headerButtons');
var $menuDropdown = $('#headerDropdown');
var $menuTrigger = $('#dropdownTrigger');
var $menuContent = $('#dropdownContent');

var $ctx;
var colorRows = [];
var rowHeight = 120;
var animFrames = 135;
var updateIndex = 0;
var numChange = 3;
var animPaused = false;
var unpauseAnim;

var colors = [
    {r:000,g:169,b:194}, //turquoise            'rgba(0, 169, 194, 1)'
    {r:000,g:099,b:176}, //blue                 'rgba(0, 99, 176, 1)'
    {r:097,g:192,b:212}, //light turquoise      'rgba(97, 192, 212, 1)'
    {r:015,g:059,b:127}, //dark blue            'rgba(15, 59, 127, 1)'
    {r:064,g:161,b:218}, //light blue           'rgba(64, 161, 218, 1)'
    {r:012,g:041,b:073}  //default background   'rgba(12,41,73,1)'
];

var $packery = $grid.packery({
    itemSelector: '.grid-item',
    columnWidth: 160,
    isFitWidth: true,
    stamp: '.stamp'
});
var prevGridHeight = $grid.height();
var resizeEvent;
var openElement = null;

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
        setTimeout(function(){
            $packery.packery('fit', event.currentTarget);
            setTimeout(function(){
                $('html, body').animate({
                  scrollTop: item.offset().top - 120
                }, 1000);
            }, 250);
        }, 250);
    }

    openElement = isExpanded ? null : event.currentTarget;
});

$(window).resize(function (){
    $bg.height = $grid.height();
    $bg.width = $(window).innerWidth();

    animPaused = true;
    clearTimeout(unpauseAnim);
    unpauseAnim = setTimeout(function() {
        animPaused = false;
        for(var r = 0; r < colorRows.length; r++){
            colorRows[r].c1 = colors.length - 1;
            colorRows[r].c2 = Math.floor(Math.random() * (colors.length - 1));
            colorRows[r].frame = 0;
        }
    }, 300);

    clearTimeout(resizeEvent);
    resizeEvent = setTimeout(function () {
        $packery.packery();
    }, 250);

    if($(window).innerWidth() > 720){
        $menuContent.slideUp();
    }
});

function gridResize() {
    if($grid.height() != prevGridHeight){
        $bg.height = $grid.height();
        $bg.width = $(window).innerWidth();
        prevGridHeight = $grid.height();
    }

    setTimeout(gridResize, 200);
}

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

function colorName(index){
    return 'rgba(' + colors[index].r + ',' + colors[index].g + ',' + colors[index].b + ',1)';
}

function lerpColor(c1, c2, frame){
    var r = Math.round(colors[c1].r + (colors[c2].r - colors[c1].r) * frame / animFrames);
    var g = Math.round(colors[c1].g + (colors[c2].g - colors[c1].g) * frame / animFrames);
    var b = Math.round(colors[c1].b + (colors[c2].b - colors[c1].b) * frame / animFrames);
    return 'rgba(' + r + ',' + g + ',' + b + ',1)';
}

$(function(){
    gridResize();
    anim_init();
});

function anim_init(){
    $bg.height = $grid.height(); //120 * Math.ceil($(window).innerHeight() / 120);
    $bg.width = $(window).innerWidth();

    $ctx = $bg.getContext("2d");
    $ctx.fillStyle = '#0c2949';
    $ctx.fillRect(0, 0, $bg.width, $bg.height);

    for(var y = 0; y < Math.ceil($bg.height / rowHeight); y++){
        init_row(y);
    }

    window.requestAnimationFrame(anim_draw);
}

function init_row(i) {
    colorRows[i] = {
        c1: colors.length - 1,
        c2: Math.floor(Math.random() * (colors.length - 1)),
        frame: Math.floor(Math.random() * animFrames)
    };
}

function reset_row(i){
    colorRows[i].c1 = colorRows[i].c2;
    while(colorRows[i].c2 == colorRows[i].c1){
        colorRows[i].c2 = Math.floor(Math.random() * (colors.length - 1));
    }
    colorRows[i].frame = 0;
}

function anim_draw() {
    if($(window).innerWidth() >= 705 && !animPaused) {
        var changed = [];

        for (var r = 0; r < numChange; r++) {
            var y;
            if(Math.ceil($bg.height / rowHeight) > numChange) {
                do {
                    y = Math.floor(Math.random() * Math.ceil($bg.height / rowHeight));
                } while (changed.indexOf(y) != -1);
                changed[updateIndex] = y;
                updateIndex = (updateIndex + 1) % numChange;
            } else {
                y = r;
            }

            if (colorRows[y] == undefined) {
                init_row(y);
            }
            if (colorRows[y].frame >= animFrames) {
                reset_row(y);
            }

            $ctx.fillStyle = lerpColor(colorRows[y].c1, colorRows[y].c2, colorRows[y].frame);
            $ctx.fillRect(0, y * rowHeight, $bg.width, rowHeight);
            (colorRows[y].frame)++;
        }
    }

    requestAnimationFrame(anim_draw);
}