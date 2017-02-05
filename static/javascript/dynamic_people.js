$person = $('.person');
$people = $('.dynamic-people');
$bubble = $('#bubble');

var headerScroll = 100;

$(window).scroll(function() {
    var scrollValue = Math.max($(this).scrollTop(), 0);
    var screenHeight = $(this).innerHeight();
    var screenWidth = $(this).innerWidth();
    var multiplier = scrollValue / headerScroll;
    if (multiplier < 1) {
    	$person.css("margin-left", screenWidth * 0.055 * (1 - multiplier) + "vw");
    	$person.css("margin-right", screenWidth * 0.055 * (1 - multiplier) + "vw");
    } else {
    	$person.css("margin-left", "0");
    	$person.css("margin-right", "0");
    	
    }
    $bubble.css("opacity", multiplier - .2);
});