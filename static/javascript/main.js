var grid = document.querySelector('.grid');
var packery = new Packery(grid, {
    columnWidth: 160,
    isFitWidth: true
});
var prevWidth = $(window).width();
var resizeEvent;
var openElement = null;

/*
 * Do we want to limit it so that only one tile can be expanded?
 * i.e. contract the previously expanded tile while expanding the new one?
 */
grid.addEventListener('click', function (event) {
    // don't proceed if item was not clicked on
    if (!matchesSelector(event.target, '.grid-item')) {
        if (!matchesSelector(event.target, '.stamp')) {
            return;
        }
    }
    if ($(event.target).data("expandable") != 1) {
        return;
    }

    if (openElement !== null) {
        packery.unstamp(openElement);
        openElement.classList.toggle('grid-item-expand');
        openElement.classList.toggle('stamp');
        openElement.classList.toggle('grid-item');
        if (openElement === event.target) {
            openElement = null;
            setTimeout(function () {
                packery.layout();
            }, 200);
            return;
        }
        openElement = null;
    }
    // change size of item via class
    packery.stamp(event.target);
    event.target.classList.toggle('grid-item-expand');
    event.target.classList.toggle('stamp');
    event.target.classList.toggle('grid-item');
    openElement = event.target;
    // trigger layout
    setTimeout(function () {
        packery.layout();
    }, 200);
});

$(window).resize(function () {
    clearTimeout(resizeEvent);
    resizeEvent = setTimeout(function () {
        //console.log("done with delay");
        packery.layout();
    }, 200);
});

packery.on('layoutComplete', function(event, items){
    console.log($('.grid').height());
    $('body').css('height', $('.grid').height());
});

/*
//Potential fancy animated background, WIP
var colors = [
    'rgba(28, 165, 170, 1)', //turquoise
    'rgba(24, 101, 174, 1)', //blue
    'rgba(120, 204, 203, 1)', //light turquoise
    'rgba(14, 46, 98, 1)', //dark blue
    'rgba(33, 144, 203, 1)' //light blue
];
var canvas;
var ctx;

$(function(){
    anim_init();
});

function anim_init(){
    canvas = document.querySelector('bgCanvas');
    ctx = canvas.getContext("2d");
    ctx.fillStyle = '#0c2949';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    window.requestAnimationFrame(anim_draw);
}

function anim_draw(){
    for(var y = 0; y < Math.floor(canvas.height / 160); y++){
        
    }
}
    */