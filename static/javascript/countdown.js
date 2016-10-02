var hackingStarts = new Date("2016-10-08T04:00:00.000Z");
var hsCountdown = $(".countdown[data-cdNum='1']");
var devpostEnds = new Date("2016-10-09T13:00:00.000Z");
var deCountdown = $(".countdown[data-cdNum='2']");
var hackingEnds = new Date("2016-10-09T16:00:00.000Z");
var heCountdown = $(".countdown[data-cdNum='3']");

hsCountdown.countdown(hackingStarts.getTime(), {elapse: false, defer: true})
    .on('update.countdown', function(event){
        $(this).html(event.strftime(
            '<h3>Hacking Begins In</h3>' +
            '<span>%D : %H : %M : %S</span>'
        ));
    })
    .on('finish.countdown', function(event){
        deCountdown.removeClass('hideCountdown');
        heCountdown.removeClass('hideCountdown');
        hsCountdown.addClass('hideCountdown');
    })
    .countdown('resume');

deCountdown.countdown(devpostEnds.getTime(), {elapse: false, defer: true})
    .on('update.countdown', function(event){
        $(this).html(event.strftime(
            '<h3>Devpost Submissions Close In</h3>' +
            '<span>%I : %M : %S</span>'
        ));
    })
    .on('finish.countdown', function(event){
        $(this).html('<h3>Devpost Submissions are Closed!</h3>');
    })
    .countdown('resume');

heCountdown.countdown(hackingEnds.getTime(), {elapse: false, defer: true})
    .on('update.countdown', function(event){
        $(this).html(event.strftime(
            '<h3>Hacking Ends In</h3>' +
            '<span>%I : %M : %S</span>'
        ));
    })
    .on('finish.countdown', function(event){
        deCountdown.remove();
        $(this).html('<h1>Hacking Is Over!</h1>');
    })
    .countdown('resume');