var announcements = [];
var aContainer = $(".announcements-container");

$(document).ready(function(){
    getAnnouncements();

    // Issues could occur with keeping announcements sorted - worth the overhead?
    //setTimeout(updateAnnouncements(), 300000);
});

function getAnnouncements(){
    $.ajax({
        url : "/v1/announcements",
        type: "GET",
        dataType: "json",
        success: function(response){
            response.results.forEach(function(a){
                if(a.approved) {
                    announcements[a.id] = {
                        title: a.title,
                        info: a.info,
                        time: new Date(a.broadcast_at * 1000),
                        category: a.category
                    };
                } else {
                    announcements[a.id] = "Unapproved Announcement";
                }
            });
            console.log(response.results);
        },
        complete: function(response){
            announcements.sort(announcementSorter);
            console.log(announcements);
            displayAnnouncements();
        },
        error: function(xhr, errmsg, err){
            console.error("Encountered Error: " + errmsg + "\n" + xhr.status + ": " + xhr.responseText);
        }
    });
}

function announcementSorter(a, b){
    return b.time - a.time;
}

function formatDate(d){
    var days = ["Friday", "Saturday", "Sunday"];
    return days[(d.getDay() + 2) % 7] + ", " + (d.getHours() % 12) + ":" + ("0" + d.getMinutes()).slice(-2) + (d.getHours() >= 12 ? "pm" : "am");
}

function displayAnnouncements(){
    announcements.forEach(function(a, idx){
        if(a !== "Unapproved Announcement") {
            aContainer.append(
                "<div class='announcement' data-id='" + idx + "'>" +
                "<h2>" + a.title + "</h2>" +
                "<h3>" + formatDate(a.time) + "</h3>" +
                "<p>" + a.info + "</p>" +
                "</div>"
            );
        }
    });
}

function displayAnnouncement(idx){
    var a = announcements[idx];
    aContainer.append(
        "<div class='announcement' data-id='" + idx + "'>" +
        "<h2>" + a.title + "</h2>" +
        "<h3>" + formatDate(a.time) + "</h3>" +
        "<p>" + a.info + "</p>" +
        "</div>"
    );
}

function updateAnnouncements(){
    $.ajax({
        url : "/v1/announcements",
        type: "GET",
        dataType: "json",
        success: function(response){
            response.results.forEach(function(a){
                if(a.approved) {
                    var newAnnouncement = {
                        title: a.title,
                        info: a.info,
                        time: new Date(a.broadcast_at * 1000),
                        category: a.category
                    };
                    if(announcements[a.id] != newAnnouncement){
                        announcements[a.id] = newAnnouncement;
                        $(".announcement[data-id='" + a.id + "']").remove();
                        displayAnnouncement(a.id);
                    }
                } else {
                    announcements[a.id] = "Unapproved Announcement";
                    $(".announcement[data-id='" + a.id + "']").remove();
                }
            });

            console.log(response);
        },
        error: function(xhr, errmsg, err){
            console.error("Encountered Error: " + errmsg + "\n" + xhr.status + ": " + xhr.responseText);
        }
    });
}