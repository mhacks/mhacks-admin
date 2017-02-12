/**
 * Created by Connor Krupp on 2/2/17.
 */

$( function() {
    $( '.form-full .full-widget input[type="checkbox"]').parent().parent().addClass('checkbox-form-container');

    $( "#school-autocomplete" ).autocomplete({
        source: COLLEGES
    });

    $( "#major-autocomplete" ).autocomplete({
        source: MAJORS
    });

    $( "#gender-autocomplete" ).autocomplete({
        source: GENDERS
    });

    $( "#race-autocomplete" ).autocomplete({
        source: RACES
    });

    $( "#state-autocomplete" ).autocomplete({
        source: STATES
    });
} );
$(document).ready(function() {
    function updateHighSchoolField() {
        var gradDateContainer = $("#graduation_date").parent();
        var majorContainer = $("#major-autocomplete").parent();
        var schoolField = $("#school-autocomplete");
        if (document.getElementById('id_is_high_school').checked) {
            gradDateContainer.hide();
            majorContainer.hide();
            schoolField.attr('placeholder', 'High School');
            schoolField.prev().text('High School');
        }
        else{
            gradDateContainer.show();
            majorContainer.show();
            schoolField.attr('placeholder', 'Hackathon College');
            schoolField.prev().text('University');
        }
    }
    
    // On form load, check if high school is already checked (if editing submitted app)
    updateHighSchoolField();
    
    document.getElementById('id_is_high_school').addEventListener('change', function() {
        updateHighSchoolField();
    });
    
    $('input[type="checkbox"][id="id_is_international"]').change(function() {
        var stateAutocomplete = $("#state-autocomplete" );
        if (this.checked) {
            stateAutocomplete.autocomplete("destroy");
            stateAutocomplete.removeData('autocomplete');
            stateAutocomplete.placeholder = "Country";
        }
        else {
            stateAutocomplete.autocomplete({
                source: STATES
            });
            stateAutocomplete.placeholder = "State";
        }
    });
    $("#id_can_pay").parent().hide();
    $('input[type="checkbox"][id="id_needs_reimbursement"]').change(function() {
        if (this.checked) {
            $("#id_can_pay").parent().show();
        }
        else{
            $("#id_can_pay").parent().hide();
        }
    });
});
