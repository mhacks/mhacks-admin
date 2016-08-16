var $menuTrigger = $('#dropdownTrigger');
var $menuContent = $('#dropdownContent');

$menuContent.css("display", "none");

$menuTrigger.click(function(){
    $menuContent.slideToggle();
});