var $packery = $('.grid').packery({
    itemSelector: '.grid-item',
    columnWidth: 160,
    isFitWidth: true,
    stamp: '.stamp'
});
var resizeEvent;
var openElement = null;
var rowBG = [];

var container = $('#container');

/*
 * Do we want to limit it so that only one tile can be expanded?
 * i.e. contract the previously expanded tile while expanding the new one?
 */
$packery.on('click', '.grid-item, .grid-item-expand', function(event){
    var item = $(event.currentTarget);

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
    canvas = document.querySelector('#bgCanvas');
    canvas.height = (container.height() < window.innerHeight) ? window.innerHeight : container.height();
    canvas.width = container.width();

    clearTimeout(resizeEvent);
    resizeEvent = setTimeout(function () {
        //console.log("done with delay");
        $packery.packery();
    }, 250);
});

//Potential fancy animated background, WIP
var colors = [
    {r:028,g:165,b:170}, //turquoise 'rgba(28, 165, 170, 1)'
    {r:024,g:101,b:174}, //blue 'rgba(24, 101, 174, 1)'
    {r:120,g:204,b:203}, //light turquoise 'rgba(120, 204, 203, 1)'
    {r:014,g:046,b:098}, //dark blue 'rgba(14, 46, 98, 1)'
    {r:033,g:144,b:203} //light blue 'rgba(33, 144, 203, 1)'
];
var canvas;
var ctx;
var rowHeight = 120;

$(function(){
    anim_init();
});

function anim_init(){
    canvas = document.querySelector('#bgCanvas');

    canvas.height = (container.height() < window.innerHeight) ? window.innerHeight : container.height();
    canvas.width = container.width();

    ctx = canvas.getContext("2d");
    ctx.fillStyle = '#0c2949';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    for(var y = 0; y < Math.ceil(canvas.height / rowHeight); y++){
        var cIndex = Math.floor(Math.random() * colors.length);
        var c1 = colors[cIndex];
        var c2 = colors[Math.floor(Math.random() * colors.length)];
        var duration = Math.floor(Math.random() * 4 + 4) * 30;
        rowBG.push({
            framesLeft: duration,
            currentColor: c1,
            colorDelta: {
                r:(c2.r-c1.r)/duration,
                g:(c2.g-c1.g)/duration,
                b:(c2.b-c1.b)/duration
            },
            colorIndex: cIndex
        });
    }

    window.requestAnimationFrame(anim_draw);
}

function anim_draw(){
    for(var y = 0; y < Math.ceil(canvas.height / rowHeight); y++){
        (rowBG[y].framesLeft)--;
        rowBG[y].currentColor = {
            r: rowBG[y].currentColor.r + rowBG[y].colorDelta.r,
            g: rowBG[y].currentColor.g + rowBG[y].colorDelta.g,
            b: rowBG[y].currentColor.b + rowBG[y].colorDelta.b
        };

        var newColor = 'rgba('+Math.floor(rowBG[y].currentColor.r)+','+Math.floor(rowBG[y].currentColor.g)+','+Math.floor(rowBG[y].currentColor.b)+',1)';
        ctx.fillStyle = newColor;
        ctx.fillRect(0, y * rowHeight, canvas.width, rowHeight);
        
        if(rowBG[y].framesLeft == 0){
            var duration = Math.floor(Math.random() * 4 + 4) * 30;
            rowBG[y].framesLeft = duration;
            var c1 = rowBG[y].currentColor;
            var newIndex = Math.floor(Math.random() * colors.length);
            while(newIndex == rowBG[y].colorIndex){
                newIndex = Math.floor(Math.random() * colors.length);
            }
            var c2 = colors[newIndex];
            rowBG[y].colorDelta = {
                r:(c2.r-c1.r)/duration,
                g:(c2.g-c1.g)/duration,
                b:(c2.b-c1.b)/duration
            }
            rowBG[y].colorIndex = newIndex;
        }
    }

    requestAnimationFrame(anim_draw);
}