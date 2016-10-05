$(".faq-item .question").click(function(event){
    var q = $(event.target);
    q.toggleClass("open");
    $(".faq-item .answer[data-qid='" + q.data("qid") + "']").stop().slideToggle('medium');
});