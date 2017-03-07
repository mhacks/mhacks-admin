/**
 * Created by Omkar on 2/15/2017.
 */

var options = {
    legend: {
        labels: {
            fontSize: 16
        }
    },
    responsive: false
};

$(document).ready(function(){
    getApplicationBreakdown();
    getRaceBreakdown();
    getGenderBreakdown();
    getSchoolBreakdown();
});

function getApplicationBreakdown() {
    $.ajax({
        url : "/v1/application_breakdown",
        type: "GET",
        dataType: "json",
        success: function(response){
            var data = {
                labels: ["Accepted", "Waitlisted", "Declined"],
                datasets: [
                    {
                        data: [response.accepted, response.waitlisted, response.declined],
                        backgroundColor: ["#58CB4C", "#CBC341", "#CB5645"],
                        hoverBackgroundColor: ["#48AD3D", "#ADA535", "#AD4D3C"]
                    }
                ]
            };

            var applicationPieCanvas = $("#application-pie");
            drawPie(applicationPieCanvas, data, options);

            $("#total-applications").text("Total applications submitted: " + response.total_applications);
            $("#total-reimbursement").text("Total reimbursement given: $" + Number(response.total_reimbursement).toFixed(2));
            $("#avg-reimbursement").text("Average reimbursement: $" + Number(response.avg_reimbursement).toFixed(2) + "/hacker");
        },
        error: function(xhr, errmsg, err){
            console.error("Encountered Error: " + errmsg + "\n" + xhr.status + ": " + xhr.responseText);
        }
    });
}

function getRaceBreakdown() {
    $.ajax({
        url : "/v1/race_breakdown",
        type: "GET",
        dataType: "json",
        success: function(response){
            var data = getDataAndLabels(response, "blue");
            var racePieCanvas = $("#race-pie");
            drawPie(racePieCanvas, data, options);
        },
        error: function(xhr, errmsg, err){
            console.error("Encountered Error: " + errmsg + "\n" + xhr.status + ": " + xhr.responseText);
        }
    });
}

function getGenderBreakdown() {
    $.ajax({
        url : "/v1/gender_breakdown",
        type: "GET",
        dataType: "json",
        success: function(response){
            var data = getDataAndLabels(response, "green");
            var genderPieCanvas = $("#gender-pie");
            drawPie(genderPieCanvas, data, options);
        },
        error: function(xhr, errmsg, err){
            console.error("Encountered Error: " + errmsg + "\n" + xhr.status + ": " + xhr.responseText);
        }
    });
}

function getSchoolBreakdown() {
    $.ajax({
        url : "/v1/school_breakdown",
        type: "GET",
        dataType: "json",
        success: function(response){
            var data = getDataAndLabels(response, "purple");
            var schoolPieCanvas = $("#school-pie");
            var optionsResponsive = options;
            optionsResponsive.responsive = true;
            drawPie(schoolPieCanvas, data, optionsResponsive);
        },
        error: function(xhr, errmsg, err){
            console.error("Encountered Error: " + errmsg + "\n" + xhr.status + ": " + xhr.responseText);
        }
    });
}

function drawPie(canvas, data, options) {
    new Chart(canvas,
        {
            type: 'pie',
            data: data,
            options: options
        }
    );
}

function getDataAndLabels(response, hue) {
    if (typeof(hue)==='undefined') hue = "random";

    var data = {
        labels: [],
        datasets: [
            {
                data: [],
                backgroundColor: randomColor({count: response.length, hue: hue})
            }
        ]
    };

    response.forEach(function (item) {
        if (item.label == "Race" || item.label == "Gender") {
            data.labels.push("N/A")
        } else {
            data.labels.push(item.label);
        }
        data.datasets[0].data.push(item.count);
    });

    return data;
}