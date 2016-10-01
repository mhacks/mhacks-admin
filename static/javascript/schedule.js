var eventsDiv = $(".events");
var eventsArea = $(".time-lines");
var timeStamps = $(".time-stamps");
var numEvents = [];
var placedEvents = [];
var doResizeEvents;
var numLines = 107;
var baseTime = new Date("2016-10-07T19:00:00.000Z");
var endTime = new Date("2016-10-10T00:00:00.000Z");

var events = [{startTime: "2016-10-07T20:00:00.000Z", endTime: "2016-10-07T21:30:00.000", name: "Event Name", description:"This is an event.", category: "0"},
              {startTime: "2016-10-07T20:30:00.000Z", endTime: "2016-10-07T23:30:00.000", name: "Event Name", description:"This is an event.", category: "0"},
              {startTime: "2016-10-07T22:20:00.000Z", endTime: "2016-10-07T23:10:00.000", name: "Event Name", description:"This is an event.", category: "0"}];

$(document).ready(function(){
    var currentTime = new Date();
    if(3600000 * Math.floor(currentTime / 3600000) > baseTime){
        baseTime = 3600000 * Math.floor(currentTime / 3600000);
    }
    numLines = (endTime - baseTime) / 1800000 + 1;
    numLines = (numLines < 0) ? 0 : numLines;

    drawMarkers();

    for(var i = 0; i < numLines; ++i){
        numEvents[i] = 0;
        placedEvents[i] = 0;
    }
    parseAllEvents();

    events.forEach(function(e){
        if(!e.expired) {
            var p = getPosition(e);
            console.log(e.rawOffset + "\t" + e.rawHeight);

            var width = numEvents[Math.floor(e.rawOffset)];
            for (var i = Math.floor(e.rawOffset) + 1; i < Math.ceil(e.rawOffset + e.rawHeight); ++i) {
                if (numEvents[i] > width) {
                    width = numEvents[i];
                }
            }

            var offset = -1;
            for (i = 0; offset == -1 && i < width; ++i) {
                var validSpot = true;
                for (var j = Math.floor(e.rawOffset); validSpot && j < Math.ceil(e.rawOffset + e.rawHeight); ++j) {
                    if ((1 << i) & placedEvents[j] == (1 << i)) {
                        validSpot = false;
                    }
                }
                if (validSpot) {
                    offset = i;
                    for (j = Math.floor(e.rawOffset); j < Math.ceil(e.rawOffset + e.rawHeight); ++j) {
                        placedEvents[j] += (1 << i);
                    }
                }
            }

            if (offset == -1) {
                console.error("Error placing event:");
                console.error(e);
                return;
            } else {
                ++offset;
            }

            console.log(offset + "\t" + width);

            eventsDiv.append("<div class='event width-" + width + " offset-" + offset + "' style='top:" + p.offset + "px; min-height: " + p.height + "px'><h2>" + e.name + "</h2><p>" + e.description + "</p></div>");
        }
    });
    resizeEvents();
    console.log(numEvents);
});

$(window).resize(function(){
    clearTimeout(doResizeEvents);
    doResizeEvents = setTimeout(resizeEvents(), 100);
});

function parseAllEvents(){
    events.forEach(function(e){
        var start = new Date(e.startTime);
        var end = new Date(e.endTime);

        if(end >= baseTime) {
            if(start < baseTime){
                start = baseTime;
            }

            e.expired = false;

            e.rawOffset = (start.getTime() - baseTime.getTime()) / 1800000;
            e.rawHeight = (end.getTime() - start.getTime()) / 1800000;

            for (var i = Math.floor(e.rawOffset); i < Math.ceil(e.rawOffset + e.rawHeight); ++i) {
                numEvents[i]++;
            }
        } else {
            e.expired = true;
        }
    });
}

function getPosition(e){
    console.log(eventsArea.offset().top);
    var pixelOffset = eventsArea.offset().top + 40 * e.rawOffset + Math.ceil(e.rawOffset / 2) * 4 + Math.floor(e.rawOffset / 2) * 2;
    var pixelHeight = 40 * e.rawHeight - 10;
    if(Math.ceil(e.rawOffset) % 2 == 0){
        pixelHeight +=  Math.ceil(e.rawHeight / 2) * 4 + Math.floor(e.rawHeight / 2) * 2;
    } else {
        pixelHeight +=  Math.ceil(e.rawHeight / 2) * 2 + Math.floor(e.rawHeight / 2) * 4;
    }

    return {offset: pixelOffset, height: pixelHeight};
}

function resizeEvents(){
    var width = eventsArea.width() - 2 * (150 - timeStamps.width());
    $(".width-1").css("width", width + "px");
    $(".width-2").css("left", (150 + Math.floor(width * 0.04)) + "px");
    $(".width-2").css("width", Math.floor(width * 0.48) + "px");
    $(".width-3").css("left", (150 + Math.floor(width * 0.035)) + "px");
    $(".width-3").css("width", Math.floor(width * 0.31) + "px");
    $(".offset-1").css("left", "150px");

    console.log(width);
}

function drawMarkers(){
    var hour = baseTime.getHours();
    var am = (hour < 12);
    var day = 0;
    for(var i = 0; i < numLines; ++i){
        eventsArea.append("<div></div>");
        if(i % 2 == 0){
            var time = "";
            if(i == 0 || hour == 0){
                switch(day){
                    case 0:
                        time += "Fri ";
                        break;
                    case 1:
                        time += "Sat ";
                        break;
                    case 2:
                        time += "Sun ";
                        break;
                }
            }
            time += ((hour % 12 == 0) ? 12 : (hour % 12)) + ":00 ";
            time += (am) ? "AM" : "PM";
            timeStamps.append("<p>" + time + "</p>");

            ++hour;
            if(hour % 12 == 0){
                am = !am;
            }
            if(hour >= 24){
                hour -= 24;
                ++day;
            }
        } else {
            timeStamps.append("<p></p>");
        }
    }

    /*$(".container").css("height", $(".time-markers").css("height"));*/
    eventsDiv.css("top", "-" + ($(".container").height() - 17) + "px");
}