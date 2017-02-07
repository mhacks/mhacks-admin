var $person = $('.person');
var $people = [$('#p1'), $('#p2'), $('#p3'), $('#p4'), $('#p5'), $('#p6'), $('#p7'), $('#p8')];
var $bubble = $('#bubble');

var animStart = 100;
var headerScroll = 300;
var animStops = [
    {s: animStart, l: headerScroll - animStart},
    {s: animStart + (headerScroll - animStart) / 4, l: (headerScroll - animStart) * 0.75},
    {s: animStart + (headerScroll - animStart) / 2, l: (headerScroll - animStart) * 0.5},
    {s: animStart + 3 * (headerScroll - animStart) / 4, l: (headerScroll - animStart) * 0.25}
    ];
var finalPos = [26, 19, 9, 5, -5, -18, -21, -32];

var isMobile = false; //initiate as false
// device detection
if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent)
    || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0,4))) isMobile = true;

$(window).scroll(function() {
    var scrollValue = Math.max($(this).scrollTop(), 0);

    if(!isMobile) {
        if (scrollValue > animStart) {
            if (scrollValue > headerScroll) {
                $person.each(function (i, p) {
                    $(p).css("transform", "translate(" + finalPos[$(p).data("place")] + "%,0)");
                });
                $bubble.css("opacity", 1);
            } else {
                $people[3].css("transform", "translate(calc(" + (1 - (scrollValue - animStops[0].s) / animStops[0].l) + " * -50vw + " + finalPos[3] + "%),0)");
                $people[4].css("transform", "translate(calc(" + (1 - (scrollValue - animStops[0].s) / animStops[0].l) + " * 50vw + " + finalPos[4] + "%),0)");
                if (scrollValue > animStops[1].s) {
                    $people[2].css("transform", "translate(calc(" + (1 - (scrollValue - animStops[1].s) / animStops[1].l) + " * -50vw + " + finalPos[2] + "%),0)");
                    $people[5].css("transform", "translate(calc(" + (1 - (scrollValue - animStops[1].s) / animStops[1].l) + " * 50vw + " + finalPos[5] + "%),0)");
                    if (scrollValue > animStops[2].s) {
                        $people[1].css("transform", "translate(calc(" + (1 - (scrollValue - animStops[2].s) / animStops[2].l) + " * -50vw + " + finalPos[1] + "%),0)");
                        $people[6].css("transform", "translate(calc(" + (1 - (scrollValue - animStops[2].s) / animStops[2].l) + " * 50vw + " + finalPos[6] + "%),0)");
                        if (scrollValue > animStops[3].s) {
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
            $person.each(function (i, p) {
                var direction = (i < $person.length / 2) ? "-50vw" : "50vw";
                $(p).css("transform", "translate(" + direction + ",0)");
            });
            $bubble.css("opacity", 0);
        }
    }
});