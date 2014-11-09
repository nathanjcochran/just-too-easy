$(document).ready(function() {
    $(".btn-shot-type").click(function(){
        var buttonGroup = $(this).parent();
        var data = {
            game_key : buttonGroup.data("game"),
            player_key : buttonGroup.data("player"),
            shot_type_key  : $(this).data("shot-type"),
        };

        $.ajax({
            type: "POST",
            dataType : "json",
            url:"/game/play",
            data : data,
            success : function(data, textStatus) {
                redScore = $("#red-score");
                redScore.css("width", data.red_score_percentage + "%");
                redScore.text(data.red_score);

                blueScore = $("#blue-score");
                blueScore.css("width", data.blue_score_percentage + "%");
                blueScore.text(data.blue_score);

                modal = buttonGroup.parents(".modal").modal('toggle');
            },
            error : function(data, textStatus, errorThrown) {
                alert("Error!" + textStatus + errorThrown);
            }
        });
    });
});
