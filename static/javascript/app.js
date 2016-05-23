'use strict';

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
// ^^^ pulled straight from the django website ^^^
$(function() {
    // Input alignment
    var alignment = function() {
        var desiredWidth = $("#longest").width() + 1;
        $(".input_word").width(desiredWidth);
    };
    $(window).resize(alignment);
    alignment();
});
