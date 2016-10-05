'use strict';

var $bg = document.querySelector('#bgCanvas');
var $grid = $('.grid');
var $ctx;
var colorRows = [];
var rowHeight = 120;
var animationFrames = 135;
var updateIndex = 0;
var numChange = 3;
var animationPaused = false;
var resumeAnimation;

var colors = [
    {r:0,  g:169,b:194}, // turquoise            'rgba(0, 169, 194, 1)'
    {r:0,  g:99, b:176}, // blue                 'rgba(0, 99, 176, 1)'
    {r:97, g:192,b:212}, // light turquoise      'rgba(97, 192, 212, 1)'
    {r:15, g:59, b:127}, // dark blue            'rgba(15, 59, 127, 1)'
    {r:64, g:161,b:218}, // light blue           'rgba(64, 161, 218, 1)'
    {r:12, g:41, b: 73}  // default background   'rgba(12,41,73,1)'
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
    }

    var isExpanded = item.hasClass('grid-item-expand');
    item.toggleClass('grid-item-expand');
    item.toggleClass('grid-item');

    if(isExpanded){
        // was expanded, now shrinking
        setTimeout(function(){
            $packery.packery('layout');
        }, 250);
    } else {
        // is expanding
        $packery.packery('fit', event.currentTarget);
        $packery.packery('stamp', item);
        $packery.packery('layout');
        $packery.packery('unstamp', item);
        $('html, body').animate({
            scrollTop: item.offset().top - 120
        }, 1000);
    }

    openElement = isExpanded ? null : event.currentTarget;
});

$(window).resize(function (){
    $bg.height = $grid.height();
    $bg.width = $(window).innerWidth();

    animationPaused = true;
    clearTimeout(resumeAnimation);
    resumeAnimation = setTimeout(function() {
        animationPaused = false;
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
});

function gridResize() {
    if($grid.height() != prevGridHeight){
        $bg.height = $grid.height();
        $bg.width = $(window).innerWidth();
        prevGridHeight = $grid.height();
    }

    setTimeout(gridResize, 200);
}

function lerpColor(c1, c2, frame){
    var r = Math.round(colors[c1].r + (colors[c2].r - colors[c1].r) * frame / animationFrames);
    var g = Math.round(colors[c1].g + (colors[c2].g - colors[c1].g) * frame / animationFrames);
    var b = Math.round(colors[c1].b + (colors[c2].b - colors[c1].b) * frame / animationFrames);
    return 'rgba(' + r + ',' + g + ',' + b + ',1)';
}

$(function(){
    gridResize();
    initializeAnimation();
});

function initializeAnimation() {
    $bg.height = $grid.height(); //120 * Math.ceil($(window).innerHeight() / 120);
    $bg.width = $(window).innerWidth();

    $ctx = $bg.getContext("2d");
    $ctx.fillStyle = '#0c2949';
    $ctx.fillRect(0, 0, $bg.width, $bg.height);

    for(var y = 0; y < Math.ceil($bg.height / rowHeight); y++){
        initializeRow(y);
    }

    window.requestAnimationFrame(drawAnimation);
}

function initializeRow(rowNumber) {
    colorRows[rowNumber] = {
        c1: colors.length - 1,
        c2: Math.floor(Math.random() * (colors.length - 1)),
        frame: Math.floor(Math.random() * animationFrames)
    };
}

function resetRow(rowNumber){
    colorRows[rowNumber].c1 = colorRows[rowNumber].c2;
    while(colorRows[rowNumber].c2 == colorRows[rowNumber].c1){
        colorRows[rowNumber].c2 = Math.floor(Math.random() * (colors.length - 1));
    }
    colorRows[rowNumber].frame = 0;
}

function drawAnimation() {
    if($(window).innerWidth() >= 705 && !animationPaused) {
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
                initializeRow(y);
            }
            if (colorRows[y].frame >= animationFrames) {
                resetRow(y);
            }

            $ctx.fillStyle = lerpColor(colorRows[y].c1, colorRows[y].c2, colorRows[y].frame);
            $ctx.fillRect(0, y * rowHeight, $bg.width, rowHeight);
            (colorRows[y].frame)++;
        }
    }

    requestAnimationFrame(drawAnimation);
}