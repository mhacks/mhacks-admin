var $person = $('.person');
var $people = [$('#p1'), $('#p2'), $('#p3'), $('#p4'), $('#p5'), $('#p6'), $('#p7'), $('#p8')];
var $bubble = $('#bubble');

var animStart = 60;
var headerScroll = 160;
var animStops = [
    {s: animStart, l: headerScroll - animStart},
    {s: animStart + (headerScroll - animStart) / 4, l: (headerScroll - animStart) * 0.75},
    {s: animStart + (headerScroll - animStart) / 2, l: (headerScroll - animStart) * 0.5},
    {s: animStart + 3 * (headerScroll - animStart) / 4, l: (headerScroll - animStart) * 0.25}
    ];
var finalPos = [26, 19, 9, 5, -5, -18, -21, -32];

$(window).scroll(function() {
    var scrollValue = Math.max($(this).scrollTop(), 0);

    if(scrollValue > animStart){
        if(scrollValue > headerScroll){
            $person.each(function(i, p){
                $(p).css("transform", "translate(" + finalPos[$(p).data("place")] + "%,0)");
            });
            $bubble.css("opacity", 1);
        } else {
            $people[3].css("transform", "translate(calc(" + (1 - (scrollValue - animStops[0].s) / animStops[0].l) + " * -50vw + " + finalPos[3] + "%),0)");
            $people[4].css("transform", "translate(calc(" + (1 - (scrollValue - animStops[0].s) / animStops[0].l) + " * 50vw + " + finalPos[4] + "%),0)");
            if(scrollValue > animStops[1].s){
                $people[2].css("transform", "translate(calc(" + (1 - (scrollValue - animStops[1].s) / animStops[1].l) + " * -50vw + " + finalPos[2] + "%),0)");
                $people[5].css("transform", "translate(calc(" + (1 - (scrollValue - animStops[1].s) / animStops[1].l) + " * 50vw + " + finalPos[5] + "%),0)");
                if(scrollValue > animStops[2].s){
                    $people[1].css("transform", "translate(calc(" + (1 - (scrollValue - animStops[2].s) / animStops[2].l) + " * -50vw + " + finalPos[1] + "%),0)");
                    $people[6].css("transform", "translate(calc(" + (1 - (scrollValue - animStops[2].s) / animStops[2].l) + " * 50vw + " + finalPos[6] + "%),0)");
                    if(scrollValue > animStops[3].s){
                        $people[0].css("transform", "translate(calc(" + (1 - (scrollValue - animStops[3].s) / animStops[3].l) + " * -50vw + " + finalPos[0] + "%),0)");
                        $people[7].css("transform", "translate(calc(" + (1 - (scrollValue - animStops[3].s) / animStops[3].l) + " * 50vw + " + finalPos[7] + "%),0)");
                    } else {
                        $people[0].css("transform", "translate(-50vw,0)");
                        $people[7].css("transform", "translate(50vw,0)");
                    }
                } else {
                    $people[1].css("transform", "translate(-50vw,0)");
                    $people[6].css("transform", "translate(50vw,0)");
                }
            } else {
                $people[2].css("transform", "translate(-50vw,0)");
                $people[5].css("transform", "translate(50vw,0)");
            }
            $bubble.css("opacity", (scrollValue - animStops[0].s) / animStops[0].l);
            /*$person.each(function(i, p){
                var direction = (i < $person.length / 2) ? "-50vw" : "50vw";
                $(p).css("transform", "translate(calc(" + (1 - (scrollValue - 60) / 100) + " * " + direction + " + " + finalPos[$(p).data("place")] + "%),0)");
            });*/
        }
    } else {
        $person.each(function(i, p){
            var direction = (i < $person.length / 2) ? "-50vw" : "50vw";
            $(p).css("transform", "translate(" + direction + ",0)");
        });
        $bubble.css("opacity", 0);
    }
});