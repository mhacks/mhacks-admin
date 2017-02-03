$person = $('.person');
$people = $('.dynamic-people');
$bubble = $('#bubble');

$(window).scroll(function() {
    var scrollValue = Math.max($(this).scrollTop(), 0);
    var screenHeight = $(this).outerHeight();
    var screenWidth = $(this).outerWidth();
    var multiplier = scrollValue / screenHeight;
    if (multiplier < 1) {
    	$person.css("margin-left", screenWidth * 0.055 * (1 - multiplier) + "%");
    	$person.css("margin-right", screenWidth * 0.055 * (1 - multiplier) + "%");
    } else {
    	$person.css("margin-left", "0%");
    	$person.css("margin-right", "0%");
    	
    }
    $bubble.css("opacity", multiplier - .2);
});