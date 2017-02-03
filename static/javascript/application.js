/**
 * Created by Connor Krupp on 2/2/17.
 */

$( function() {
    $('input[type="checkbox"]').parent().parent().addClass('checkbox-form-container');

    $( "#school-autocomplete" ).autocomplete({
        source: COLLEGES
    });

    $( "#major-autocomplete" ).autocomplete({
        source: MAJORS
    });

    $( "#gender-autocomplete" ).autocomplete({
        source: GENDER_PRONOUNS
    });

    $( "#race-autocomplete" ).autocomplete({
        source: RACES
    });

    $( "#state-autocomplete" ).autocomplete({
        source: STATES
    });
} );
$(document).ready(function() {
    $('input[type="checkbox"][id="id_is_high_school"]').change(function() {
        if (this.checked) {
            $("#graduation_date").parent().hide();
            $("#major-autocomplete").parent().hide();
            $("#school-autocomplete").attr('placeholder', 'High School');
            $("#school-autocomplete").prev().text('High School');
        }
        else{
            $("#graduation_date").parent().show();
            $("#major-autocomplete").parent().show();
            $("#school-autocomplete").attr('placeholder', 'Hackathon College');
            $("#school-autocomplete").prev().text('University');
        }
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
